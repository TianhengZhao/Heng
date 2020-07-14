from flask_login import login_user
from flask import request, Blueprint, g, jsonify, url_for
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from ..extensions import db
from werkzeug.security import generate_password_hash
from ..model import User  # model引用必须在db和login_manager之后，以免引起循环引用

auth_bp = Blueprint('auth', __name__)
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()


@auth_bp.route('/signinData',methods=['GET', 'POST'])                   # methods要加上，默认只接受GET方法
def signinData():
    data = request.get_json()
    if validate_name(data['username']) is False:   # 用户名不唯一
        return 'Wrong Name'
    else :
        if validate_email(data['email']) is False:  # 邮箱不唯一
            return 'Wrong Email'
        else:
            user0 = User(username=data['username'],email=data['email'])
            user0.set_password(data['password'])
            db.session.add(user0)
            db.session.commit()
            response = jsonify(user0.to_dict())
            response.status_code = 201
            # HTTP协议要求201响应包含一个值为新资源URL的Location头部
            response.headers['Location'] = url_for('user.get_user', id=user0.id)
            return response


# 验证用户名和密码（basic_anth，不产生token）
@auth_bp.route('/loginData',methods=['GET', 'POST'])
def login():
    data = request.get_json()
    que = User.query.filter_by(username=data['username']).first()
    if que is not None and que.validate_password(data['password']):                      # 用户是否存在
        g.current_user = que                  # 将该用户赋给 g.current_user
        login_user(que)
        return g.current_user.generate_token(86400)                         # token有效期设置为1天
    else:
        return 'false'


@auth_bp.route('/getToken', methods=['GET'])
def get_token():
    token = g.current_user.generate_token(600)
    db.session.commit()
    return token


@token_auth.verify_token
def varify_token(token):
    g.current_user = User.validate_token(token) if token else None
    return g.current_user is not None


def validate_email(data):               # 检查数据库中是否有相同邮箱
   if User.query.filter_by(email=data).first():
       return False


def validate_name(data):               # 检查数据库中是否有相同用户名
   if User.query.filter_by(username=data).first():
       return False


