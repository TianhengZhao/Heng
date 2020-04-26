from flask import request,Blueprint,jsonify
from flask_cors import CORS
from ..extensions import db
from ..model import user  # model引用必须在db和login_manager之后，以免引起循环引用
user_bp = Blueprint('user', __name__)


@user_bp.route('/<id>',methods=['GET'])
def get_user(id):
     return jsonify(user.query.get_or_404(id).to_dict())  # 使用jsonify序列化处理
