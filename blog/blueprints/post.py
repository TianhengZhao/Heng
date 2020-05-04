from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from ..extensions import db
from flask import Blueprint, request, g
#from .error import bad_request
from ..model import post

post_bp = Blueprint('post', __name__)


@post_bp.route('/add', methods=['POST'])
def add_post():                       # 添加新文章
    data = request.get_json()
    '''if not data:
        return bad_request('please send JSON data')'''

    posts = post()
    posts.from_dict(data)
    posts.author = g.current_user
    db.session.add(posts)
    db.session.commit()
    return 'Sucess'
