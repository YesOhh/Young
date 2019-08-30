#!/usr/bin/python
# -*- coding: UTF-8 -*-
# ===========================================================
#      Author : yxu
#       Email :
#        Date : 
# Description : 
#        Args : 
# ===========================================================

from flask import Blueprint, flash, redirect, url_for, render_template
from young.decorators import admin_required
from young.forms.post import CategoryForm, EditCategoryForm
from young.models import Category, Comment, Post
from young.extensions import db
from young.utils import redirect_back


admin_bp = Blueprint('admin', __name__)


@admin_bp.before_request
@admin_required
def admin_protect():
    pass


@admin_bp.route('/category/manage', methods=['GET'])
def manage_category():
    form = EditCategoryForm()
    cfrom = CategoryForm()
    return render_template('admin/manage_category.html', form=form, cform=cfrom)


@admin_bp.route('/post/manage', methods=['GET'])
def manage_post():
    posts = Post.query.all()
    return render_template('admin/manage_post.html', posts=posts)


@admin_bp.route('/category/new', methods=['POST'])
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('分类创建成功！', 'success')
        return redirect_back()
    flash('分类名已存在或输入错误！', 'warning')
    return redirect(url_for('.manage_category'))


@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
def del_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('分类删除成功！', 'warning')
    return redirect_back()


@admin_bp.route('/category/<int:category_id>/edit', methods=['POST'])
def edit_category(category_id):
    form = EditCategoryForm()
    if form.validate_on_submit():
        new_category_name = form.name.data
        category = Category.query.get_or_404(category_id)
        category.name = new_category_name
        db.session.commit()
        flash('分类修改完成！', 'success')
        return redirect_back()
    flash('分类名已存在或输入错误', 'warning')
    return redirect_back()


@admin_bp.route('/comment/delete/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('评论删除成功！', 'success')
    return redirect_back()


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
def del_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('文章删除成功', 'success')
    return redirect_back()
