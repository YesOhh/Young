#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 
#        Args : 
# ===========================================================

from flask import (
    Blueprint,
    flash,
    render_template,
    redirect,
    url_for
)
from flask_login import (
    current_user,
    logout_user,
    login_user,
    login_required,
    login_fresh,
    confirm_login
)
from young.forms.auth import (
    LogInForm,
    RegisterForm,
    ForgetPasswordForm,
    ResetPasswordForm
)
from young.models import User
from young.utils import (
    redirect_back,
    generate_token,
    validate_token
)
from young.extensions import db
from young.settings import Operation
from young.emails import send_confirm_email, send_reset_password_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.validate_password(form.password.data):
            login_user(user=user, remember=form.remember.data)
            # flash('登录成功！', 'info')
            return redirect_back()
        flash('账号或密码错误！', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        username = form.username.data
        name = form.name.data
        password = form.password.data
        user = User(username=username, name=name, email=email)
        user.set_password(password=password)
        db.session.add(user)
        db.session.commit()
        token = generate_token(user=user, operation=Operation.CONFIRM)
        send_confirm_email(user=user, token=token)
        flash('确认邮件已发送，请注意查收邮箱！', 'info')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    # flash('登出成功！', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    if validate_token(user=current_user, token=token, operation=Operation.CONFIRM):
        flash('账号验证成功！', 'info')
        return redirect(url_for('main.index'))
    else:
        flash('Token错误或已经超时！', 'danger')
        return redirect(url_for('.resend_confirm_email'))


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('main.index'))

    token = generate_token(user=current_user, operation=Operation.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('新的确认邮件已发送，请注意查收邮件！', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/re_authenticate', methods=['GET', 'POST'])
@login_required
def re_authenticate():
    if login_fresh():
        return redirect(url_for('main.index'))

    form = LogInForm()
    if form.validate_on_submit() and current_user.validate_password(form.password.data):
        confirm_login()
        return redirect_back()
    return render_template('auth/login.html', form=form)


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_token(user=user, operation=Operation.RESET_PASSWORD)
            send_reset_password_email(user=user, token=token)
            flash('重置密码邮件已发送，请注意查收邮件！', 'info')
            return redirect(url_for('.login'))
        flash('邮箱错误！', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            flash('邮箱输入错误！', 'warning')
            return redirect(url_for('.reset_password', token=token))
        if validate_token(user=user, token=token, operation=Operation.RESET_PASSWORD, new_password=form.password.data):
            flash('密码重置成功！', 'success')
            return redirect(url_for('.login'))
        else:
            flash('Token错误或已经超时！', 'danger')
            return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.html', form=form)
