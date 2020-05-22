from base64 import b64encode
from datetime import datetime, timedelta
from flask import jsonify
import json
import re
import unittest
from blog import create_app, db
from blog.model import user, article


class APITestCase(unittest.TestCase):
    def setUp(self):
        '''每个测试之前执行'''
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()  # Flask内建的测试客户端，模拟浏览器行为

    def tearDown(self):
        '''每个测试之后执行'''
        db.session.remove()
        db.drop_all()  # 删除所有数据库表
        self.app_context.pop()  # 退出Flask应用上下文

    """
    def test_404(self):
        # 测试请求不存在的API时
        response = self.client.get('/auth/wrong')
        self.assertEqual(response.status_code, 404)
       json_response = json.loads(response.get_data(as_text=True))
       self.assertEqual(json_response['error'], 'Not Found')
    """

    # 创建Basic Auth认证的headers
    def get_basic_auth_headers(self, username, password):
        return{
            'Authorization': 'Basic' + b64encode((username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    # 创建有token认证的headers
    def get_token_auth_headers(self, username, password):
        headers = self.get_basic_auth_headers(username, password)
        response = self.client.post('/auth/loginData')                 # 产生该用户的token
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(json_response.get('token'))
        token = json_response['token']
        return {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    """def test_signin_login(self):
        data = jsonify({
            'username': 'zhao',
            'email': 'zhao@163.com',
            'password': '123'
        })
        response = self.client.post('/auth/signinData',data)
        self.assertEqual(response.status_code, 302)

        # 输入错误的用户密码
        #headers = self.get_basic_auth_headers('zhao', '12345')
        #response = self.client.post('/auth/loginData', headers = headers)
        #self.assertEqual(response.status_code, 401)"""

