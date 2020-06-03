from flask import Blueprint, jsonify, g
from ..model import notification
from .post import error_response
from .auth import token_auth

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('notification/<id>', methods=['GET'])
@token_auth.login_required
def get_notification(id):
    que = notification.query.get_or_404(id)
    if g.current_user != que.author:
        return error_response(403)
    data = que.to_dict()
    return jsonify(data)