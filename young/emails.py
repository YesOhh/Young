#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 用于发送邮件
#        Args : 
# ===========================================================

from flask_mail import Message
from young.extensions import mail
from threading import Thread
from flask import (
    current_app,
    render_template
)
import os
import sendgrid
from sendgrid.helpers.mail import Email as SGEmail, Content, Mail as SGMail


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['MAIL_PREFIX'] + ' ' + subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


# send over SendGrid Web API
# def send_api_mail(subject, to, template, **kwargs):
#     sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
#     from_email = SGEmail('Grey Li <noreply@helloflask.com>')
#     to_email = SGEmail(to)
#     body = render_template(template + '.txt', **kwargs)
#     content = Content("text/plain", body)
#     email = SGMail(from_email, subject, to_email, content)
#     sg.client.mail.send.post(request_body=email.get())


def send_confirm_email(user, token, to=None):
    send_mail(to=to or user.email, subject='验证邮件', template='emails/confirm', user=user, token=token)
    # send_api_mail(to=to or user.email, subject='验证邮件', template='emails/confirm', user=user, token=token)


def send_change_email_email(user, token, to=None):
    send_mail(subject='修改邮箱确认', to=to or user.email, template='emails/change_email', user=user, token=token)
    # send_api_mail(subject='修改邮箱确认', to=to or user.email, template='emails/change_email', user=user, token=token)


def send_reset_password_email(user, token):
    send_mail(subject='修改密码确认', to=user.email, template='emails/reset_password', user=user, token=token)
    # send_api_mail(subject='修改密码确认', to=user.email, template='emails/reset_password', user=user, token=token)
