"""
    author: Tianheng Zhao
    应用的配置文件
"""
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) # 返回.py文件的绝对路径

class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'   # 待修改
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = 'HengBlog'
    FLASKY_MAIL_SENDER = 'Heng'
    FLASKY_ADMIN = os.environ.get('<1146824110@qq.com>')
    SSL_REDIRECT = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):   # 继承Config类
    SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}/{}'.format('mysql', 'pymysql', 'root','root', 'localhost',
                                                                         'HengDev')


class TestingConfig(BaseConfig):     # 不太懂test什么意思
    TESTING = True
    SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}/{}'.format('mysql', 'pymysql', 'root','root', '127.0.0.1',
                                                                         'HengTest')
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}/{}'.format('mysql', 'pymysql', 'ubuntu','1', 'localhost:3306',
                                                                         'hengblog')


Config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}