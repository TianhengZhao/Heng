from flask import Blueprint
from .auth import token_auth

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('notification/<id>', methods=['GET'])
@token_auth.login_required
def get_notification(id):