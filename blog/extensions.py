"""
    存放引入的包，并且声明
"""
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_avatars import Avatars
from flask_migrate import Migrate
avatars = Avatars()
bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
moment = Moment()
csrf = CSRFProtect()
migrate = Migrate()


# @login_manager.user_loader
# def load_user(user_id):       # 建立 user_loader 的回调函数，该函数通过 user_id 来获取 user 对象
#    from blog.model import user    # 避免循环引用
#    User = user.query.get(int(user_id))
#    return User              # 调用current_user时调用此函数返回当前用户对象
