#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 
#        Args : 
# ===========================================================

from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length
from young.models import Category


class PostForm(FlaskForm):
    """文章表单"""
    title = StringField('标题', validators=[DataRequired(), Length(1, 60)])
    category = SelectField('分类', coerce=int, default=1)
    body = CKEditorField('文本', validators=[DataRequired()])
    submit = SubmitField('发布')

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    """分类表单"""
    name = StringField('名称', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField('创建')

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('该分类已经存在')


class CommentForm(FlaskForm):
    """评论表单"""
    # 登录用户直接显示用户的昵称，非登录游客考虑限制评论。两种情况均不需要填写
    # name = StringField('昵称', validators=[DataRequired(), Length(1, 30)])
    body = TextAreaField('评论', validators=[DataRequired()])
    submit = SubmitField('提交')


class ReplyForm(FlaskForm):
    """回复评论表单"""
    # 登录用户直接显示用户的昵称，非登录游客考虑限制评论。两种情况均不需要填写
    # name = StringField('昵称', validators=[DataRequired(), Length(1, 30)])
    body = TextAreaField('回复', validators=[DataRequired()])
    submit = SubmitField('提交')


class EditCategoryForm(FlaskForm):
    """编辑分类表单"""
    name = StringField('新名称', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField('修改')

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('该分类已经存在')
