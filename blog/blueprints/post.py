from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from ..extensions import db
from flask import Blueprint, request

post_bp = Blueprint('post', __name__)


@post_bp.route('/post', methods=['POST'])
def add_post():                       # 添加新文章
    data = request.get_json()