#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 
#        Args : 
# ===========================================================

import os


class Operation:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', '72212e82eb6444d586b98eb171c15f73')
    SESSION_COOKIE_NAME = os.getenv('SESSION_COOKIE_NAME', 'updateframe_session')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '748166112@qq.com')
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Young Blog', os.environ.get('MAIL_USERNAME'))
    MAIL_PREFIX = 'Young Blog'
    YOUNG_BLOG_PER_PAGE = 8
    YOUNG_BLOG_FOLLOWING_PER_PAGE = 20
    WHOOSHEE_MIN_STRING_LEN = 1
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024
    AVATARS_SAVE_PATH = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'upload_avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{os.environ.get("DATABASE_USERNAME")}:{os.environ.get("DATABASE_PASSWORD")}@{os.environ.get("DATABASE_HOST")}:{os.environ.get("DATABASE_PORT")}/{os.environ.get("DATABASE_NAME")}?charset=utf8'


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{os.environ.get("DATABASE_USERNAME")}:{os.environ.get("DATABASE_PASSWORD")}@{os.environ.get("DATABASE_HOST")}:{os.environ.get("DATABASE_PORT")}/{os.environ.get("DATABASE_NAME")}?charset=utf8'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
