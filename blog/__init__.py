"""
    blog应用包的构造文件，定义工厂函数
"""
import os
from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import bootstrap, db, login_manager, mail, avatars, migrate
from .model import user
from .blueprints.auth import auth_bp
from .blueprints.user import user_bp
from .blueprints.post import post_bp
from .blueprints.comment import comment_bp
from .blueprints.notification import notification_bp


def create_app(config_name=None):
    """
    工厂函数
    :param config_name: 应用使用的配置名
    :return: 应用实例app
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)   # WSGI将接收自客户端的所有请求转交给该Flask对象处理
    CORS(app)                                               # 解决跨域问题
    app.config.from_object(Config[config_name])
    register_extensions(app)  # 应用配置好后初始化扩展
    register_blueprints(app)
    return app


def register_extensions(app):
    """初始化扩展"""
    login_manager.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    avatars.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(post_bp, url_prefix='/post')
    app.register_blueprint(comment_bp, url_prefix='/comment')
    app.register_blueprint(notification_bp, url_prefix='/notification')


