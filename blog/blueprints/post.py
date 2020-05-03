from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from ..extensions import db
from flask import Blueprint, request
from .error import bad_request
from ..model import post

post_bp = Blueprint('post', __name__)


@post_bp.route('/post', methods=['POST'])
def add_post():                       # 添加新文章
    data = request.get_json()
    if not data:
        return bad_request('please send JSON data')
    message = {}
    if 'title' not in data or not data.get('title'):
        message['title'] = 'Title is required.'
    elif len(data.get('title')) > 255:
        message['title'] = 'Title must less than 255 characters.'
    if 'body' not in data or not data.get('body'):
        message['body'] = 'Body is required.'
    if message:
        return bad_request(message)

    posts = post()
    posts.to_dict(data)
