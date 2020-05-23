from .auth import token_auth
from flask import Blueprint, request, g, jsonify, url_for
from ..extensions import db
from werkzeug.http import HTTP_STATUS_CODES

from ..model import article, comment

post_bp = Blueprint('post', __name__)


# 添加新文章
@post_bp.route('/add', methods=['POST'])
@token_auth.login_required
def add_post():
    data = request.get_json()
    posts = article()
    posts.from_dict(data)
    posts.author = g.current_user
    db.session.add(posts)
    db.session.commit()
    response = jsonify(posts.to_dict())
    response.status_code = 201  # 201(已创建)请求成功并且服务器创建了新的资源
    response.headers['Location'] = url_for('post.get_post', id=posts.id)  # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    return response


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
    per_page = 5
    pagi = article.pagnitede_dict(article.query.filter_by(author_id = id).order_by(article.timestamp.desc()), page, per_page, 'post.get_ones_posts', id=id)
    return jsonify(pagi)


# 获取文章id的所有评论
@post_bp.route('/getComments/<id>', methods=['GET'])
def get_comments(id):
    page = request.args.get('page', 1, type=int)
    per_page = 5
    post = article.query.get_or_404(id)
    data = comment.pagnitede_dict(post.comments.filter(comment.parent==None).order_by(comment.timestamp.desc()),  page, per_page, 'post.get_comments', id=id)  # 获得一级评论
    for item in data['items']:                              # 对于page中的每一项
        com = comment.query.get(item['id'])
        descendants = [child.to_dict() for child in com.get_descendants()]    # 得到该评论的所有子孙评论
        from operator import itemgetter
        item['descendants'] = sorted(descendants, key=itemgetter('timestamp'))  # 按 timestamp 排序一个字典列表
    return jsonify(data)


def error_response(status_code, message=None):     # 返回状态码及信息
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}     # ？？？
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@post_bp.app_errorhandler(404)
def not_found_error(error):
    return error_response(404)


@post_bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return error_response(500)






