import unittest
from flask import current_app
from blog import create_app, db

# 测试用例，最小的测试单元
class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        '''每个测试之前执行'''
        self.app = create_app('testing')  # 创建Flask应用
        self.app_context = self.app.app_context()  # 激活(或推送)Flask应用上下文
        self.app_context.push()
        db.create_all()  # db.create_all()快速创建所有的数据库表

    def tearDown(self):
        '''每个测试之后执行'''
        db.session.remove()
        db.drop_all()  # 删除所有数据库表
        self.app_context.pop()  # 退出Flask应用上下文

    def test_app_exists(self):
        '''测试程序实例是否存在'''
        self.assertFalse(current_app is None)  # 断言方法

    def test_app_is_testing(self):
        '''测试配置TESTING是否为true'''
        self.assertTrue(current_app.config['TESTING'])