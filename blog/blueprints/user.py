from .auth import token_auth
from flask import request, Blueprint, jsonify, g
from ..extensions import db
from ..model import user, article  # model引用必须在db和login_manager之后，以免引起循环引用
user_bp = Blueprint('user', __name__)


@user_bp.route('/<id>', methods=['GET'])  # 返回id对应的用户信息
@token_auth.login_required
def get_user(id):
     que = user.query.get_or_404(id)
     if g.current_user == que:
          return jsonify(que.to_dict())    # 如果查询自己的信息
     data = que.to_dict()
     data['is_following'] = g.current_user.is_following(que)     # 如果是查询其它用户，添加 是否已关注过该用户 的标志位
     return jsonify(data)


@user_bp.route('/<id>', methods=['PUT'])  # 修改id对应的用户信息
def update(id):
     data = request.get_json()
     que = user.query.get_or_404(id)
     que.about_me = data['about_me']
     que.sex = data['sex']
     db.session.add(que)
     db.session.commit()
     return 'Success'


@user_bp.route('/follow/<id>', methods=['GET'])
@token_auth.login_required
def follow(id):
     que = user.query.get_or_404(id)
     if g.current_user == que:
          return 'Wrong'
     if g.current_user.is_following(que):
          return 'Wrong'
     g.current_user.follow(que)
     db.session.commit()
     return 'Success'


@user_bp.route('/unfollow/<id>', methods=['GET'])
@token_auth.login_required
def unfollow(id):
     que = user.query.get_or_404(id)
     if g.current_user == que:
          return 'Wrong'
     if not g.current_user.is_following(que):
          return 'Wrong'
     g.current_user.unfollow(que)
     db.session.commit()
     return 'Success'


# 获得用户id的所有粉丝
@user_bp.route('/getOnesFans/<id>', methods=['GET'])
def get_ones_fans(id):
    que = user.query.get_or_404(id)                 # 得到id对应的用户que
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagi = user.pagnitede_dict(que.followers, page, per_page, 'user.get_ones_fans', id=id)  # que.followers得到que的所有粉丝，分页
    return jsonify(pagi)



