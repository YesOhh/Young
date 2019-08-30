#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 
#        Args : 
# ===========================================================

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    ValidationError,
    HiddenField
)
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    Regexp
)
from young.models import User
from flask_wtf.file import FileField, FileAllowed, FileRequired


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='用户名不能为空'), Length(4, 16),
                                              Regexp('^[a-zA-Z0-9]*$', message='用户名只能包含大小写字母和数字')])
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不能为空'), Length(1, 254), Email()])
    name = StringField('昵称', validators=[DataRequired(message='昵称不能为空'), Length(2, 24)])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空'), Length(6, 64, message='密码长度为6至64位'),
                                               EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='密码不能为空')])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱已被使用')


class LogInForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(message='登陆名不能为空'), Length(1, 254)])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空'), Length(6, 64, message='密码长度为6至64位')])
    remember = BooleanField('记住密码')
    submit = SubmitField('登录')


class EditProfileForm(FlaskForm):
    name = StringField('昵称', validators=[DataRequired(message='昵称不能为空'), Length(2, 24)])
    location = StringField('所在地')
    submit = SubmitField('提交')


class ChangeEmailForm(FlaskForm):
    email = StringField('新邮箱', validators=[DataRequired(message='邮箱不能为空'), Length(1, 254), Email()])
    submit = SubmitField('提交')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired(message='密码不能为空')])
    password = PasswordField('新密码', validators=[DataRequired(message='密码不能为空'), Length(6, 64, message='密码长度为6至64位'),
                                                EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='密码不能为空')])
    submit = SubmitField('提交')


class ForgetPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不能为空'), Length(1, 254), Email()])
    submit = SubmitField('提交')


class ResetPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(message='邮箱不能为空'), Length(1, 254), Email()])
    password = PasswordField('新密码', validators=[DataRequired(message='密码不能为空'), Length(6, 64, message='密码长度为6至64位'),
                                                EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired(message='密码不能为空')])
    submit = SubmitField('提交')


class UploadAvatarForm(FlaskForm):
    image = FileField('上传头像', validators=[FileRequired(), FileAllowed(['jpg', 'png'], '允许上传的文件为jpg、png')])
    submit = SubmitField('上传')


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('裁剪并上传')
