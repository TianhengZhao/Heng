from flask_login import login_user
from flask import request, Blueprint, g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from ..extensions import db
from werkzeug.security import generate_password_hash
from ..model import user  # model引用必须在db和login_manager之后，以免引起循环引用
auth_bp = Blueprint('auth', __name__)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@auth_bp.route('/loginData',methods=['GET', 'POST'])                   # methods要加上，默认只接受GET方法
def loginData():
    data = request.get_json()
    que = user.query.filter_by(username=data['username']).first()
    if que is not None and que.validate_password(data['password']):   # 验证密码
        login_user(que, remember=data['rem'])
        token = que.generate_token(6000)
        return token
    else:
        return 'Wrong'


@auth_bp.route('/signinData',methods=['GET', 'POST'])                   # methods要加上，默认只接受GET方法
def signinData():
    data = request.get_json()
    if validate_name(data['username']) is False:   # 用户名不唯一
        return 'Wrong Name'
    else :
        if validate_email(data['email']) is False:  # 邮箱不唯一
            return 'Wrong Email'
        else:
            password_hash = generate_password_hash(data['password'], method='pbkdf2:sha256',salt_length=8)
            user0 = user(username=data['username'],email=data['email'],password_hash=password_hash)
            db.session.add(user0)
            db.session.commit()
            return 'Success'       # 必须有返回值


@token_auth.verify_token
def varify_token(token):
    g.current_user = user.validate_token(token) if token else None
    return g.current_user is not None


def validate_email(data):               # 检查数据库中是否有相同邮箱
   if user.query.filter_by(email=data).first():
       return False


def validate_name(data):               # 检查数据库中是否有相同用户名
   if user.query.filter_by(username=data).first():
       return False