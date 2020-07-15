"""
消息通知API
"""
from flask import Blueprint, jsonify, g
from ..model import Notification
from .post import error_response
from .auth import token_auth

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('notification/<id>', methods=['GET'])
@token_auth.login_required
def get_notification(id):
    """获得消息通知"""
    que = Notification.query.get_or_404(id)
    if g.current_user != que.author:
        return error_response(403)
    data = que.to_dict()
    return jsonify(data)
