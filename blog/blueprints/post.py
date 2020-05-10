from .auth import token_auth
from flask import Blueprint, request, g, jsonify
from ..extensions import db
#from .error import bad_request
from ..model import article

post_bp = Blueprint('post', __name__)


@post_bp.route('/add', methods=['POST'])
@token_auth.login_required
def add_post():                       # 添加新文章
    data = request.get_json()
    '''if not data:
        return bad_request('please send JSON data')'''
    posts = article()
    posts.from_dict(data)
    posts.author = g.current_user
    db.session.add(posts)
    db.session.commit()
    return 'Success'


@post_bp.route('/getPosts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    pagi = article.pagnitede_dict(article.query.order_by(article.timestamp.desc()), page, per_page, 'post.get_posts')
    return jsonify(pagi)


@post_bp.route('/getPost/<int:id>', methods=['GET'])
def get_post(id):
    art = article.query.get_or_404(id).to_dict()
    return art




