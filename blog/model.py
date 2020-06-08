"""
  author: Tianheng Zhao
"""
import json
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import check_password_hash
from flask import url_for
from datetime import datetime
from time import time
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


# 用户模型
class user(paginatededAPI, db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)  # 建立索引
    email = db.Column(db.String(254), unique=True, index=True)    # 建立索引
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(256))
    reg_since = db.Column(db.DateTime(), default=datetime.utcnow)
    sex = db.Column(db.String(5))
    last_received_comments_read_time = db.Column(db.DateTime)          # 上次查看新评论时间
    last_received_followers_read_time = db.Column(db.DateTime)         # 上次查看新粉丝时间
    last_received_likes_read_time = db.Column(db.DateTime)             # 上次查看新的赞时间
    last_followed_posts_read_time = db.Column(db.DateTime)             # 上次查看关注者文章时间
    posts = db.relationship('article', backref='author', lazy='dynamic', cascade='all,delete-orphan')     # user和post建立双向关系backref，user为‘一’，posts为‘多’
    comments = db.relationship('comment', backref='author', lazy='dynamic',cascade='all, delete-orphan')  #user为‘一’，comments为‘多’
    notifications = db.relationship('notification', backref='author', lazy='dynamic',cascade='all, delete-orphan')
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

    def followed_posts(self):
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

    # 用户获得的新评论的个数
    def new_received_comment(self):
        last_read_time = self.last_received_comments_read_time or datetime(1900, 1, 1)
        all_posts = [post.id for post in self.posts.all()]
        all_comments = comment.query.filter(comment.article_id.in_(all_posts), comment.author != self)
        new_comments = all_comments.filter(comment.timestamp > last_read_time).count()
        return new_comments

    # 用户新粉丝的个数
    def new_received_followers(self):
        last_read_time = self.last_received_comments_read_time or datetime(1900, 1, 1)
        new_followers = self.followers.filter(followers.c.timestamp > last_read_time).count()
        return new_followers

    # 用户新赞的个数
    def new_received_likes(self):
        last_read_time = self.last_received_likes_read_time or datetime(1900, 1, 1)
        all_comments = self.comments.join(comments_likes)
        new_likes_count = 0
        for c in all_comments:
            for u in c.likers:
                res = db.engine.execute('select * from comments_likes where user_id={} and comment_id={}'.format(u.id, c.id))
                timestamp = list(res)[0][2]
                if timestamp > last_read_time:
                    new_likes_count += 1
        return new_likes_count

    # 给用户添加新的通知
    def add_new_notification(self, name, data):
        self.notifications.filter_by(name=name).delete()
        # 为用户添加通知，写入数据库
        n = notification(name=name, payload_json=json.dumps(data), user_id=self.id)
        db.session.add(n)
        return n

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

    def generate_token(self, expire_in=None, **kwargs):  # 产生令牌
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


# 文章模型
class article(paginatededAPI, db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    summary = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))                       # 将author_id设为外键
    comments = db.relationship('comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')  # user为‘一’，comments为‘多’

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


comments_likes = db.Table(                         # 建立关联表
    'comments_likes',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow())
)


# 评论模型
class comment(paginatededAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    mark_read = db.Column(db.Boolean, default=False)                    # 评论是否已读标志位
    disabled = db.Column(db.Boolean, default=False)                       # 屏蔽评论
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))           # 将user.id设置为外键，和user形成一对多关系
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), index=True)       # 将article.id设置为外键，和article形成一对多关系
    likers = db.relationship(                                           # 评论点赞数，comment与user建立多对多关系
        'user',
        secondary=comments_likes,
        backref=db.backref('liked_comments',  lazy='dynamic'))

    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'))  # 自引用，将父评论的id设为外键
    # 级联删除定义在多的一侧，parent是“一”，children是“多”；用remote_side参数指定‘一’的一方，值为一个Colmun对象（必须唯一）
    parent = db.relationship('comment', backref=db.backref('children', cascade='all, delete-orphan'), remote_side=[id])

    def __repr__(self):
        return '<Comment {}>'.format(self.id)

    def get_descendants(self):           # 获得一级评论的所有子孙评论
        data = set()

        def descendants(comment):
            if comment.children:          # 如果该评论有子评论
                data.update(comment.children)
                for child in comment.children:
                    descendants(child)        # 递归得到comment的所有子孙评论

        descendants(self)
        return data

    def is_liked_by(self, this_user):                    # 用户是否赞过该评论
        return this_user in self.likers

    def like(self, this_user):                           # 点赞
        if not self.is_liked_by(this_user):
            return self.likers.append(this_user)

    def cancle_like(self, this_user):                   # 取消点赞
        if self.is_liked_by(this_user):
            return self.likers.remove(this_user)

    def likes_count(self):
        return len(self.likers)

    def from_dict(self, data):
        for field in ['body', 'timestamp', 'mark_read', 'disabled', 'author_id', 'article_id', 'parent_id']:
            if field in data:                          # in 判断 key in dict
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'id': self.id,
            'disabled': self.disabled,
            'body': self.body,
            'timestamp': self.timestamp,
            'likers_id': [liker.id for liker in self.likers],
            'post': self.post.to_dict(),
            'author': self.author.to_dict(),
            'parent': self.parent.to_dict() if self.parent else None,
            '_links': {
                'self': url_for('comment.get_comment', id=self.id),
                'author_url': url_for('user.get_user', id=self.author_id),
                'post_url': url_for('post.get_post', id=self.article_id),
            }
        }
        return data


class notification(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.Float, index=True, default=time)
    payload_json = db.Column(db.Text)

    def __repr__(self):
        return '<Notification {}>'.format(self.id)

    def get_data(self):
        return json.loads(str(self.payload_json))

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'payload_json': self.payload_json,
            'user': {
                'id': self.author.id,
                'username': self.author.username,
                'avatar': self.author.avatar(128)
            },
            'timestamp': self.timestamp,
            '_links': {
                'self': url_for('notification.get_notification', id=self.id),
                'user_url': url_for('user.get_user', id=self.user_id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['body', 'timestamp']:
            if field in data:
                setattr(self, field, data[field])

