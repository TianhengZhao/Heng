import os
from blog import create_app

app=create_app(None)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('blog/tests')  # 找到 tests 目录
    unittest.TextTestRunner(verbosity=2).run(tests)