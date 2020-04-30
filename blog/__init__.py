import os
from flask import Flask
from .config import Config
from .extensions import bootstrap, db, login_manager, mail,avatars,migrate
from flask_cors import CORS
from .model import user
from .blueprints.auth import auth_bp
from .blueprints.user import user_bp


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
    CORS(app)    #解决跨域问题
    app.config.from_object(Config[config_name])
    register_extensions(app)
    register_blueprints(app)
    return app


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    avatars.init_app(app)
    migrate.init_app(app,db)



def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')

