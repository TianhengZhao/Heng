from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
"""
from .post import post_bp
from ..model import db


def error_response(status_code, message=None):     # 返回状态码及信息
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}     # ？？？
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    '''400 INVALID REQUEST - [POST/PUT/PATCH]：用户发出的请求有错误，服务器没有进行新建或修改数据的操作，该操作是幂等的'''
    return error_response(400, message)

"""
