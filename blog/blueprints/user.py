from .auth import token_auth
from flask import request, Blueprint, jsonify, g, url_for
from datetime import datetime
from ..extensions import db
from .post import error_response
from operator import itemgetter
from ..model import User, Comment, comments_likes, Notification  # model引用必须在db和login_manager之后，以免引起循环引用

user_bp = Blueprint('user', __name__)


# 返回id对应的用户信息
@user_bp.route('/<id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
     que = User.query.get_or_404(id)
     if g.current_user == que:
          return jsonify(que.to_dict())    # 如果查询自己的信息
     data = que.to_dict()
     data['is_following'] = g.current_user.is_following(que)     # 如果是查询其它用户，添加 是否已关注过该用户 的标志位
     return jsonify(data)


# 修改id对应的用户信息
@user_bp.route('/<id>', methods=['PUT'])
def update(id):
     data = request.get_json()
     que = User.query.get_or_404(id)
     que.about_me = data['about_me']
     que.sex = data['sex']
     db.session.add(que)
     db.session.commit()
     return 'Success'


# 关注用户
@user_bp.route('/follow/<id>', methods=['GET'])
@token_auth.login_required
def follow(id):
     que = User.query.get_or_404(id)
     if g.current_user == que:
          return 'Wrong'
     if g.current_user.is_following(que):
          return 'Wrong'
     g.current_user.follow(que)
     que.add_new_notification('new_received_followers', que.new_received_followers())  # 更新未读通知数目
     db.session.commit()
     return 'Success'


# 取消关注
@user_bp.route('/unfollow/<id>', methods=['GET'])
@token_auth.login_required
def unfollow(id):
     que = User.query.get_or_404(id)
     if g.current_user == que:
          return 'Wrong'
     if not g.current_user.is_following(que):
          return 'Wrong'
     g.current_user.unfollow(que)
     db.session.commit()
     return 'Success'


# 获得用户id的所有粉丝
@user_bp.route('/getOnesFans/<id>', methods=['GET'])
@token_auth.login_required
def get_ones_fans(id):
    que = User.query.get_or_404(id)                 # 得到id对应的用户que
    page = request.args.get('page', 1, type=int)
    per_page = 4
    pagi = User.paginated_dict(que.followers, page, per_page, 'user.get_ones_fans', id=id)  # que.followers得到que的所有粉丝，分页
    for item in pagi['items']:
        item['is_following'] = g.current_user.is_following(User.query.get(item['id']))    # 对于que的每个粉丝item['id']，查看g.current_user是否关注过
        res = db.engine.execute("select * from followers where follower_id={} and followed_id={}".format(item['id'], que.id))   # 获得关联表中timestamp
        item['timestamp'] = list(res)[0][2]
    mark = request.args.get('mark')
    if mark == 'true':  # 字符串形式
        pagi['has_new'] = False
        que.last_received_followers_read_time = datetime.utcnow()
        for item in pagi['items']:
            item['is_new'] = False
    else:
        last_read_time = g.current_user.last_received_followers_read_time or datetime(1900, 1, 1)
        for item in pagi['items']:
            if item['timestamp'] > last_read_time:
                item['is_new'] = True
                pagi['has_new'] = True
    db.session.commit()
    return jsonify(pagi)


# 获得用户id的所有关注者（大神）
@user_bp.route('/getOnesFolloweds/<id>', methods=['GET'])
@token_auth.login_required
def get_ones_followeds(id):
    que = User.query.get_or_404(id)                 # 得到id对应的用户que
    page = request.args.get('page', 1, type=int)
    per_page = 4
    pagi = User.paginated_dict(que.followeds, page, per_page, 'user.get_ones_followeds', id=id)  # que.followers得到que的所有粉丝，分页
    for item in pagi['items']:
         item['is_following'] = g.current_user.is_following(User.query.get(item['id']))                     # 对于que的每个粉丝item['id']，查看g.current_user是否关注过
    return jsonify(pagi)


# 获得用户id得到的所有评论
@user_bp.route('/receivedComments/<id>', methods = ['GET'])
@token_auth.login_required
def get_received_comments(id):
    que = User.query.get_or_404(id)
    if que != g.current_user:
        return error_response(403)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    post_ids = [post.id for post in que.posts.all()]          # 用户发表的所有文章的id
    pagi = Comment.paginated_dict(
        Comment.query.filter(Comment.article_id.in_(post_ids), Comment.author != g.current_user).   # 得到用户所有文章的所有他人评论
            order_by(Comment.mark_read, Comment.timestamp.desc()),                                  # 将评论按未读->已读、时间倒序排序
        page, per_page, 'user.get_received_comments', id=id)
    mark = request.args.get('mark')
    if mark == 'true':           # 字符串形式
        pagi['has_new'] = False
        que.last_received_comments_read_time = datetime.utcnow()
        que.add_new_notification('new_received_comment', 0)
        for item in pagi['items']:
                item['is_new'] = False
    else:
        last_read_time = g.current_user.last_received_comments_read_time or datetime(1900, 1, 1)
        for item in pagi['items']:
            if item['timestamp'] > last_read_time:               # 当前评论时间戳大于上次查看时间，说明是新评论
                item['is_new'] = True
                pagi['has_new'] = True
    db.session.commit()
    return jsonify(pagi)


# 获得用户id得到的所有赞
@user_bp.route('/receivedLikes/<id>', methods = ['GET'])
@token_auth.login_required
def get_received_likes(id):
    que = User.query.get_or_404(id)
    if que != g.current_user:
        return error_response(403)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    comments = (que.comments.join(comments_likes)).paginate(page, per_page)           # 用户得到的所有赞分页
    records = {
        'items': [],
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': comments.pages,
            'total_items': ""
        },
        '_links': {
            'self': url_for('user.get_received_likes', page=page, per_page=per_page, id=id),
            'next': url_for('user.get_received_likes', page=page + 1, per_page=per_page,
                            id=id) if comments.has_next else None,
            'prev': url_for('user.get_received_likes', page=page - 1, per_page=per_page,
                            id=id) if comments.has_prev else None
        }
    }
    count = 0
    for c in comments.items:
        # 重组数据，变成: (谁) (什么时间) 点赞了你的 (哪条评论)
        for u in c.likers:
            data = {}
            data['author'] = u.to_dict()
            data['comment'] = c.to_dict()
            # 获取点赞时间
            res = db.engine.execute(
                "select * from comments_likes where user_id={} and comment_id={}".format(u.id, c.id))
            data['timestamp'] = list(res)[0][2]
            # 标记本条点赞记录是否为新的
            records['items'].append(data)
            count += 1
        # 按 timestamp 排序一个字典列表(倒序，最新关注的人在最前面)
    records['_meta']['total_items'] = count
    records['items'] = sorted(records['items'], key=itemgetter('timestamp'), reverse=True)
    mark = request.args.get('mark')
    if mark == 'true':           # 字符串形式
        records['has_new'] = False
        que.last_received_likes_read_time = datetime.utcnow()
        que.add_new_notification('new_received_likes', 0)
        for item in records['items']:
                item['is_new'] = False
    else:
        last_read_time = que.last_received_likes_read_time or datetime(1900, 1, 1)
        for item in records['items']:
            if item['timestamp'] > last_read_time:
                item['is_new'] = True
                records['has_new'] = True
    db.session.commit()
    return jsonify(records)


# 获得用户id关注者的文章
@user_bp.route('/followedPosts/<id>', methods = ['GET'])
@token_auth.login_required
def get_followed_posts(id):
    que = User.query.get_or_404(id)
    if que != g.current_user:
        return error_response(403)
    page = request.args.get('page', 1, type=int)
    per_page = 5
    pagi = User.paginated_dict(que.followed_posts(),page, per_page, 'user.get_followed_posts', id=id)
    return jsonify(pagi)


@user_bp.route('/hasNewNoti/<id>', methods = ['GET'])
@token_auth.login_required
def hasNewNoti(id):
    que = User.query.get_or_404(id)
    if que != g.current_user:
        return error_response(403)
    since = request.args.get('since')
    noti = que.notifications.filter(Notification.timestamp > since)
    data = [n.to_dict() for n in noti]
    return jsonify(data)









