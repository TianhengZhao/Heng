from flask_login import login_user
from flask import request,Blueprint
from flask_cors import CORS
from ..extensions import db
from ..utils import generate_token
from werkzeug.security import generate_password_hash
from ..model import user  #model引用必须在db和login_manager之后，以免引起循环引用
auth_bp = Blueprint('auth', __name__)

#cors = CORS(auth_bp, resources={"/auth/loginData/*": {"origins": "*"}})
@auth_bp.route('/loginData',methods=['GET', 'POST'])                   #methods要加上，默认只接受GET方法
def loginData():
    data = request.get_json()
    que = user.query.filter_by(username=data['username']).first()
    if que is not None and que.validate_password(data['password']):   #验证密码
        login_user(que, remember=data['rem'])
        token = generate_token(que,600)
        return token
    else:
        return 'Wrong'


#cors = CORS(auth_bp, resources={"/auth/signinData/*": {"origins": "*"}})    #要加上/auth ？？？？？
@auth_bp.route('/signinData',methods=['GET', 'POST'])                   #methods要加上，默认只接受GET方法
def signinData():
    data = request.get_json()
    if validate_name(data['username']) is False:   #用户名不唯一
        return 'Wrong Name'
    else :
        if validate_email(data['email']) is False:  #邮箱不唯一
            return 'Wrong Email'
        else:
            password_hash = generate_password_hash(data['password'], method='pbkdf2:sha256',salt_length=8)
            user0 = user(username=data['username'],email=data['email'],password_hash=password_hash)
            db.session.add(user0)
            db.session.commit()
            return 'Success'       #必须有返回值


def validate_email(data):               #检查数据库中是否有相同邮箱
   if user.query.filter_by(email=data).first():
       return False


def validate_name(data):               #检查数据库中是否有相同用户名
   if user.query.filter_by(username=data).first():
       return False