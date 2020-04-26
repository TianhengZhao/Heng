from flask import current_app
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer   #从itsdangerous（提供签名辅助类）导入JWS令牌；
from .extensions import db


def generate_token(user,expire_in=None, **kwargs):   #产生令牌
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)   #序列化对象
    data = {'id': user.id,'name':user.username}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])    #和创建令牌一样的密钥建立序列化对象
    try:
        data = s.loads(token)   #返回从playload中取出的数据
    except (SignatureExpired, BadSignature):  #签名过期或签名不匹配
        return False
    db.session.commit()
    return True
