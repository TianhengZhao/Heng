"""
文章评论操作API
"""
from flask import Blueprint, request, g, jsonify, url_for
from .auth import token_auth
from ..extensions import db
from ..model import Comment, Article

comment_bp = Blueprint('comment', __name__)


@comment_bp.route('/comments', methods=['POST'])
@token_auth.login_required
def add_comment():
    """添加新评论"""
    data = request.get_json()
    post = Article.query.get_or_404(data['article_id'])
    com = Comment()
    new_body = data['body'].strip()
    com.body = new_body.replace('\n', '')
    com.author = g.current_user
    com.post = post
    if data['parentId'] is not 0:
        com.parent_id = data['parentId']
    db.session.add(com)
    db.session.commit()
    users = set()      # 该评论添加后需要通知的用户
    users.add(com.post.author)  # 将文章作者添加进集合中，
    if Comment.parent:           # 如果该评论有父评论
        # 得到所有发表祖先评论的用户
        ancestors_authors = {c.author for c in com.get_ancestors()}
        users = users | ancestors_authors     # 得到并集
    # 给各用户发送新评论通知
    for u in users:
        u.add_new_notification('new_received_comment',
                               u.new_received_comment())
    db.session.commit()  # 更新数据库，写入新通知
    response = jsonify(com.to_dict())
    # 201(已创建)请求成功并且服务器创建了新的资源
    response.status_code = 201
    # HTTP协议要求201响应包含一个值为新资源URL的Location头部
    response.headers['Location'] = url_for('comment.get_comment', id=com.id)
    return response


@comment_bp.route('/comments/<id>', methods=['GET'])
def get_comment(id):
    """获得comment表id对应的单个评论"""
    com = Comment.query.get_or_404(id)
    return jsonify(com.to_dict())


@comment_bp.route('/comments/<id>', methods=['DELETE'])
@token_auth.login_required
def delete_com(id):
    """删除评论"""
    com = Comment.query.get_or_404(id)
    users = set()  # 该评论添加后需要通知的用户
    users.add(com.post.author)  # 将文章作者添加进集合中，
    if com.parent:  # 如果该评论有父评论
        # 得到所有发表祖先评论的用户
        ancestors_authors = {c.author for c in com.get_ancestors()}
        users = users | ancestors_authors  # 得到并集
    db.session.delete(com)
    db.session.commit()
    for u in users:
        u.add_new_notification('new_received_comment',
                               u.new_received_comment())
    db.session.commit()  # 更新数据库，写入新通知
    return 'Success'


@comment_bp.route('/comments/<id>/like', methods=['GET'])
@token_auth.login_required
def like_comment(id):
    """点赞该评论"""
    com = Comment.query.get_or_404(id)
    com.like(g.current_user)
    com.author.add_new_notification('new_received_likes', com.author.new_received_likes())
    db.session.add(com)
    db.session.commit()
    return 'Success'


@comment_bp.route('/comments/<id>/unlike', methods=['GET'])
@token_auth.login_required
def unlike_comment(id):
    """取消点赞评论"""
    com = Comment.query.get_or_404(id)
    com.cancle_like(g.current_user)
    com.author.add_new_notification('new_received_likes', com.author.new_received_likes())
    db.session.add(com)
    db.session.commit()
    return 'Success'


@comment_bp.route('/comments/<id>/disableOrEnable', methods=['PUT'])
@token_auth.login_required
def disabled_com(id):
    """屏蔽评论或者解除屏蔽"""
    data = request.get_json()
    com = Comment.query.get_or_404(id)
    com.disabled = data['disableOrEnable']
    db.session.add(com)
    db.session.commit()
    return 'Success'
