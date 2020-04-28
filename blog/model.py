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

