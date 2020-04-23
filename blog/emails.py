from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from .extensions import mail


def _send_async_mail(app, message):
    with app.app_context():  #手动激活程序上下文
        mail.send(message)   #send（）内部使用了current_app函数


def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['ALBUMY_MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()   #current_app只在激活的程序上下文中才存在
    thr = Thread(target=_send_async_mail, args=[app, message])   #异步任务队列处理
    thr.start()
    return thr


def send_confirm_email(user, token, to=None):
    send_mail(subject='Email Confirm', to=to or user.email, template='emails/confirm', user=user, token=token)