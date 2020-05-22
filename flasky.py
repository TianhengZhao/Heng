import os
from blog import create_app
import click
import os
import sys


app = create_app(None)

# 创建 coverage 实例
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='blog/*')
    COV.start()


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('blog/tests')  # 找到 tests 目录
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False, help='Run tests under code coverage.')
def test(coverage):
    '''Run the unit tests.'''
    # 如果执行 flask test --coverage，但是FLASK_COVERAGE环境变量不存在时，给它配置上
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'  # 需要字符串的值
        #sys.exit(subprocess.call(sys.argv))                                    失败，出bug
        os.execvp(sys.executable, [sys.executable]+sys.argv)                     # 成功

    import unittest
    tests = unittest.TestLoader().discover('blog/tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(os.path.join(basedir, 'tmp'), 'coverage')
        COV.html_report(directory=covdir)
        print('')
        print('HTML report be stored in: %s' % os.path.join(covdir, 'index.html'))
        COV.erase()