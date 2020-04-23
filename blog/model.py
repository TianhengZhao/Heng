"""
  author: Tianheng Zhao
"""
from flask_login import UserMixin
import jwt
from werkzeug.security import  check_password_hash
from flask import current_app
from datetime import datetime, timedelta
from .extensions import db
class user(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)  #建立索引
    email = db.Column(db.String(254), unique=True, index=True)    #建立索引
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)     #用户状态，设置默认值为false

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)  #返回值为True表示密码正确

