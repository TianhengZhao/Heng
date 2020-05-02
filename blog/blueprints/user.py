from flask import request, Blueprint, jsonify
from ..extensions import db
from ..model import user  # model引用必须在db和login_manager之后，以免引起循环引用
user_bp = Blueprint('user', __name__)


@user_bp.route('/<id>', methods=['GET'])  # 返回id对应的用户信息
def get_user(id):
     return jsonify(user.query.get_or_404(id).to_dict())  # 使用jsonify序列化处理


@user_bp.route('/<id>', methods=['PUT'])  # 修改id对应的用户信息
def update(id):
     data = request.get_json()
     que = user.query.get_or_404(id)
     que.about_me = data['about_me']
     que.sex = data['sex']
     db.session.add(que)
     db.session.commit()
     return 'Success'

