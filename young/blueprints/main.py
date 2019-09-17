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
    render_template,
    redirect,
    url_for,
    request,
    current_app,
    flash
)
from flask_login import (
    current_user,
    login_required
)
from young.models import (
    Post,
    Comment,
    Category,
    User
)
from young.forms.post import CommentForm, ReplyForm
from young.utils import redirect_back, SelfPagination

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@main_bp.route('/index')
def index():
    # if current_user.is_authenticated:
    #     page = request.args.get('page', 1, type=int)
    #     per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    #     pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    #     posts = pagination.items
    #     return render_template('main/index.html', pagination=pagination, posts=posts)
    # return render_template('main/about.html')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    posts = pagination.items
    return render_template('main/index.html', pagination=pagination, posts=posts)


@main_bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=per_page)
    posts = pagination.items
    return render_template('guest/explore.html', pagination=pagination, posts=posts)


@main_bp.route('/search')
def search():
    # 先查用户，再查文章
    q = request.args.get('q', '').strip()
    if q == '':
        return redirect_back()

    result = []
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    users = User.query.whooshee_search(q).all()
    posts = Post.query.whooshee_search(q).order_by(Post.timestamp.desc()).all()
    result.extend(users)
    result.extend(posts)
    pager_obj = SelfPagination(current_page=page, total_count=len(result), base_url=request.path, params=request.args,
                               per_page_count=per_page)
    index_list = result[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()
    return render_template('main/search.html', q=q, result=result, index_list=index_list, html=html)


@main_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    form = CommentForm()
    rform = ReplyForm()
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.asc()).paginate(page=page, per_page=per_page)
    comments = pagination.items
    return render_template('main/post.html', post=post, pagination=pagination, comments=comments, form=form, rform=rform)


@main_bp.route('/category/<category_name>/post')
def category_post(category_name):
    category = Category.query.filter_by(name=category_name).first()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('main/category_post.html', category=category, pagination=pagination, posts=posts)
