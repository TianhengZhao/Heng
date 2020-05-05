from .auth import token_auth
from ..extensions import db
from flask import Blueprint, request, g, jsonify
#from .error import bad_request
from ..model import post

post_bp = Blueprint('post', __name__)


@post_bp.route('/add', methods=['POST'])
@token_auth.login_required
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


@post_bp.route('/getPosts', methods=['GET'])
def get_posts():
    data = request.get_json()
    pagi = post.pagnitede_dict(post.query.order_by(post.timestamp.desc()), data['page'], data['per_page'], 'getPosts.get_posts')
    return jsonify(pagi)
