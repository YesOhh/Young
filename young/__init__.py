#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 工厂函数
#        Args : 
# ===========================================================

import os
import click
from flask import Flask, render_template
from young.extensions import (
    db,
    bootstrap,
    csrf,
    login_manager,
    moment,
    mail,
    ckeditor,
    avatars,
    whooshee,
)
from young.settings import config
from young.blueprints.auth import auth_bp
from young.blueprints.main import main_bp
from young.blueprints.user import user_bp
from young.blueprints.admin import admin_bp
from young.models import (
    Role,
    Category
)
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFError
import logging
from logging.handlers import RotatingFileHandler
from flask.logging import default_handler
from werkzeug.middleware.proxy_fix import ProxyFix

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')
    app = Flask('young')
    app.config.from_object(config[config_name])
    app.wsgi_app = ProxyFix(app.wsgi_app)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_template_context(app)
    register_errorhandlers(app)
    register_logger(app)
    migrate = Migrate(app, db)
    return app


def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)
    avatars.init_app(app)
    whooshee.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_commands(app):
    @app.cli.command()
    def init():
        click.echo('初始化数据库...')
        db.create_all()
        click.echo('初始化控制权限...')
        Role.init_role()
        click.echo('完成！')

    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')


def register_template_context(app):
    @app.context_processor
    def make_template_context():
        categories = Category.query.order_by(Category.name).all()
        return dict(categories=categories)


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 500


def register_logger(app):
    app.logger.setLevel(logging.INFO)
    formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s:\n%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler = RotatingFileHandler(os.path.join(BASE_DIR, 'log', 'Young.log'),
                                       maxBytes=20 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    if not app.debug:
        app.logger.addHandler(file_handler)
