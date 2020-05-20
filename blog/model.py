"""
  author: Tianheng Zhao
"""
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import check_password_hash
from flask import url_for
from datetime import datetime
from .extensions import db
from flask import current_app
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer   # 从itsdangerous（提供签名辅助类）导入JWS令牌；
from werkzeug.security import generate_password_hash


class paginatededAPI(object):
    @staticmethod
    def pagnitede_dict(query, page, per_page, endpoint, **kwargs):
        info = query.paginate(page, per_page)              # paginate实现分页功能
        data = {
            'items': [item.to_dict() for item in info.items],    # 页中每一项的内容
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': info.pages,     # 总页数
                'total_items': info.total      # 返回的记录总数
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if info.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) if info.has_prev else None
            }
        }
        return data


# 自引用多对多关系
followers = db.Table(                                 # 关联表
    'followers',                                      # 关联表的名称
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)
)


class user(paginatededAPI, db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)  # 建立索引
    email = db.Column(db.String(254), unique=True, index=True)    # 建立索引
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(256))
    reg_since = db.Column(db.DateTime(), default=datetime.utcnow)
    sex = db.Column(db.String(5))
    posts = db.relationship('article', backref='author', lazy='dynamic', cascade='all,delete-orphan')     # user和post建立双向关系
    followeds = db.relationship(
        'user',                            # 关联表名，自引用
        secondary=followers,             # 指明用于该关系的关联表
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def is_following(self, obj):
        return self.followeds.filter(followers.c.followed_id == obj.id).count() > 0     # 判断当前user是否关注obj

    def follow(self, obj):
        if not self.is_following(obj):                # 如果当前user未关注过该obj
            self.followeds.append(obj)                      # 在关联表中添加self和该obj

    def unfollow(self, obj):
        if self.is_following(obj):                    # 如果当前user关注了该obj
            self.followeds.remove(obj)                      # 在关联表中删除self对应的obj

    def followed_posts(self, obj):
        followed = article.query.join(
            followers, (followers.c.followed_id == article.author_id)    # 将关联表和文章表进行关联
        ).filter(followers.c.follower_id == self.id)                     # 找出当前用户所关注用户的文章
        return followed.order_by(article.timestamp.desc())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)  # 返回值为True表示密码正确

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()  # 以utf-8格式编码邮箱，然后得到MD5哈希值，以16进制表示
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email':self.email,
            'about_me': self.about_me,
            'reg_since': self.reg_since.isoformat() + 'Z',
            'sex':self.sex,
            '_links': {
                'self': url_for('user.get_user', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        return data

    def generate_token(self, expire_in=None, **kwargs):  # 产生令牌   这个有效时间没大搞明白？？？
        s = Serializer(current_app.config['SECRET_KEY'], expire_in)  # 序列化对象
        data = {'id': self.id, 'name': self.username}
        data.update(**kwargs)
        return s.dumps(data)

    @staticmethod                                           # 静态方法用来进行验证
    def validate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])  # 和创建令牌一样的密钥建立序列化对象
        try:
            data = s.loads(token)  # 返回从playload中取出的数据
        except (SignatureExpired, BadSignature):  # 签名过期或签名不匹配
            return None
        db.session.commit()                     # 为什么要commit？？？
        return user.query.get(data['id'])


class article(paginatededAPI, db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    summary = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))                       # 将author_id设为外键

    def __repr__(self):
        return '<Post {}>'.format(self.title)

    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'body': self.body,
            'timestamp': self.timestamp,
            'views': self.views,
            'author': self.author.to_dict(),
            '_links': {
                'self': url_for('post.get_posts', id=self.id),
                'author_url': url_for('user.get_user', id=self.author_id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['title', 'summary', 'body']:
            if field in data:
                setattr(self, field, data[field])   # setattr(object, name, value)用于设置属性
