#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 初始化各类扩展对象
#        Args : 
# ===========================================================

from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_login import LoginManager, AnonymousUserMixin
from flask_moment import Moment
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_avatars import Avatars
from flask_whooshee import Whooshee

db = SQLAlchemy()
bootstrap = Bootstrap()
csrf = CSRFProtect()
login_manager = LoginManager()
moment = Moment()
mail = Mail()
ckeditor = CKEditor()
avatars = Avatars()
whooshee = Whooshee()


@login_manager.user_loader
def loader_user(user_id):
    from young.models import User
    user = User.query.get(int(user_id))
    return user


# 此处用于当未登录用户访问了使用login_required装饰器的视图时，程序自动重定向到登陆视图并闪现一个消息提示
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录！'
login_manager.login_message_category = 'warning'

# 当用户登录状态“不新鲜”，重定向后重新登录
login_manager.refresh_view = 'auth.re_authenticate'
login_manager.needs_refresh_message_category = 'warning'
login_manager.needs_refresh_message = '为了保护账户安全，请重新登录！'


class Guest(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False

    def can(self, permission_name):
        return False


login_manager.anonymous_user = Guest