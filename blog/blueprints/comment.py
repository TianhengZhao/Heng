from .auth import token_auth
from flask import Blueprint, request, g, jsonify
from ..extensions import db
from werkzeug.http import HTTP_STATUS_CODES
from ..model import comment

comment_bp = Blueprint('comment', __name__)

#@comment_bp.route('comment/getComments/<id>', methods=['GET'])
#def get_comments(id):
