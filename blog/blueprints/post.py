"""
博客文章操作API
"""
from flask import Blueprint, request, g, jsonify, url_for
from werkzeug.http import HTTP_STATUS_CODES
from .auth import token_auth
from ..extensions import db
from ..model import Article, Comment

post_bp = Blueprint('post', __name__)


@post_bp.route('/add', methods=['POST'])
@token_auth.login_required
def add_post():
    """添加新文章"""
    data = request.get_json()
    posts = Article()
    posts.from_dict(data)
    posts.author = g.current_user
    db.session.add(posts)
    db.session.commit()
    response = jsonify(posts.to_dict())
    response.status_code = 201  # 201(已创建)请求成功并且服务器创建了新的资源
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('post.get_post', id=posts.id)
    return response


@post_bp.route('/getPosts', methods=['GET'])
def get_posts():
    """获得所有发表文章"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 3, type=int)
    pagi = Article.paginated_dict(Article.query.order_by(Article.timestamp.desc()),
                                  page, per_page, 'post.get_posts')
    return jsonify(pagi)


@post_bp.route('/getPost/<id>', methods=['GET'])
def get_post(id):
    """根据文章id获得对应文章"""
    art = Article.query.get_or_404(id)
    art.views += 1
    db.session.add(art)
    db.session.commit()
    return jsonify(art.to_dict())


@post_bp.route('/getPost/<id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(id):
    """删除文章id对应的文章"""
    art = Article.query.get_or_404(id)
    db.session.delete(art)
    db.session.commit()
    return 'Success'


@post_bp.route('/getOnesPosts/<id>', methods=['GET'])
def get_ones_posts(id):
    """根据author_id获得该作者所有文章"""
    page = request.args.get('page', 1, type=int)
    per_page = 5
    pagi = Article.paginated_dict(Article.query.filter_by(author_id=id).
                                  order_by(Article.timestamp.desc()),
                                  page, per_page, 'post.get_ones_posts', id=id)
    return jsonify(pagi)


@post_bp.route('/getComments/<id>', methods=['GET'])
def get_comments(id):
    """获取文章id的所有评论"""
    page = request.args.get('page', 1, type=int)
    per_page = 5
    post = Article.query.get_or_404(id)
    # 获得一级评论，按时间降序
    data = Comment.paginated_dict(post.comments.filter(Comment.parent == None).
                                  order_by(Comment.timestamp.desc()),
                                  page, per_page, 'post.get_comments', id=id)
    for item in data['items']:                              # 对于page中的每一项
        com = Comment.query.get(item['id'])
        # 得到该评论的所有子孙评论
        descendants = [child.to_dict() for child in com.get_descendants()]
        from operator import itemgetter
        # 按 timestamp 排序一个字典列表，按时间升序
        item['descendants'] = sorted(descendants, key=itemgetter('timestamp'))
    return jsonify(data)


def error_response(status_code, message=None):
    """返回状态码及信息"""
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


@post_bp.app_errorhandler(404)
def not_found_error(error):
    """404错误，返回响应信息"""
    return error_response(404)


@post_bp.app_errorhandler(500)
def internal_error(error):
    """404错误，回滚，返回响应信息"""
    db.session.rollback()
    return error_response(500)
