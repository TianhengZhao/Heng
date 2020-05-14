from .auth import token_auth
from flask import Blueprint, request, g, jsonify
from ..extensions import db
# from .error import bad_request

from ..model import article

post_bp = Blueprint('post', __name__)


# 添加新文章
@post_bp.route('/add', methods=['POST'])
@token_auth.login_required
def add_post():
    data = request.get_json()
    '''if not data:
        return bad_request('please send JSON data')'''
    posts = article()
    posts.from_dict(data)
    posts.author = g.current_user
    db.session.add(posts)
    db.session.commit()
    return 'Success'


# 获得所有发表文章
@post_bp.route('/getPosts', methods=['GET'])
def get_posts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    pagi = article.pagnitede_dict(article.query.order_by(article.timestamp.desc()), page, per_page, 'post.get_posts')
    return jsonify(pagi)


# 根据文章id获得对应文章
@post_bp.route('/getPost/<id>', methods=['GET'])
def get_post(id):
    art = article.query.get_or_404(id)
    art.views += 1
    db.session.add(art)
    db.session.commit()
    return jsonify(art.to_dict())


# 删除文章id对应的文章
@post_bp.route('/getPost/<id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(id):
    art = article.query.get_or_404(id)
    db.session.delete(art)
    db.session.commit()
    return 'Success'


# 根据author_id获得该作者所有文章
@post_bp.route('/getOnesPosts/<id>', methods=['GET'])
def get_ones_posts(id):
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagi = article.pagnitede_dict(article.query.filter_by(author_id = id).order_by(article.timestamp.desc()), page, per_page, 'post.get_ones_posts', id=id)
    return jsonify(pagi)



