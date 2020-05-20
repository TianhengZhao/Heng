import unittest
from blog import create_app, db
from blog.model import user


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')    # ????????????????????????????????
        self.app_contaxt = self.app.app_context()
        self.app_contaxt.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_contaxt.pop()

    def test_password_hashing(self):
        u = user(username = '蒋丞')
        u.set_password('123')
        self.assertTrue(u.validate_password('123'))
        self.assertFalse(u.validate_password('12345'))

    def test_avatar(self):
        u = user(username='蒋丞', email='jc@qq.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/8913b0685c8611f1a9769d84a6fe39c1?d=identicon&s=128'))
