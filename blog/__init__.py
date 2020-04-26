import os
from flask import Flask
from .config import Config
from .extensions import bootstrap, db, login_manager, mail
from .model import user
from .blueprints.auth import auth_bp
from .extensions import avatars

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask(__name__)
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


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')

