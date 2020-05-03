"""
  author: Tianheng Zhao
"""
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import  check_password_hash
from flask import url_for
from datetime import datetime
from .extensions import db


class user(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)  # 建立索引
    email = db.Column(db.String(254), unique=True, index=True)    # 建立索引
    password_hash = db.Column(db.String(128))
    about_me=db.Column(db.String(256))
    reg_since = db.Column(db.DateTime(), default=datetime.utcnow)
    sex=db.Column(db.String(5))

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


class post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    summary = db.Column(db.Text)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

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
                'self': url_for('post.get_post', id=self.id),
                'author_url': url_for('user.get_user', id=self.author_id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['title', 'summary', 'body']:
            if field in data:
                setattr(self, field, data[field])   # setattr(object, name, value)用于设置属性
