from .auth import token_auth
from flask import request, Blueprint, jsonify, g
from ..extensions import db
from ..model import user  # model引用必须在db和login_manager之后，以免引起循环引用
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
     que.follow(que)
     db.session.commit()
     return 'Success'



