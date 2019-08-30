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
    flash,
    request,
    current_app,
    send_from_directory
)
from flask_login import (
    current_user,
    login_required,
    fresh_login_required
)
from young.forms.post import PostForm, CommentForm, ReplyForm
from young.models import (
    Post,
    Category,
    Comment,
    User,
    Collect
)
from young.extensions import db, avatars
from young.forms.auth import EditProfileForm, ChangeEmailForm, ChangePasswordForm, UploadAvatarForm, CropAvatarForm
from young.utils import generate_token, validate_token, redirect_back, SelfPagination
from young.settings import Operation
from young.emails import send_change_email_email
from young.decorators import confirm_required

user_bp = Blueprint('user', __name__)


# @user_bp.before_request
# @login_required
# def login_protect():
#     pass


@user_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
@confirm_required
def write_articles():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category, user=current_user)
        db.session.add(post)
        db.session.commit()
        flash('文章提交成功！', 'success')
        return redirect(url_for('main.index'))
    return render_template('user/write_articles.html', form=form)


@user_bp.route('/add/comment/<int:post_id>', methods=['POST'])
@login_required
@confirm_required
def add_comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        new_comment = Comment(body=body, post_id=post_id, user=current_user)
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('main.show_post', post_id=post_id) + '#comments')


@user_bp.route('/reply/comment/<int:comment_id>', methods=['POST'])
@login_required
@confirm_required
def reply_comment(comment_id):
    form = ReplyForm()
    replied_comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get_or_404(replied_comment.post_id)
    if form.validate_on_submit():
        body = form.body.data
        new_comment = Comment(body=body, post=post, user=current_user)
        new_comment.replied = replied_comment
        db.session.add(new_comment)
        db.session.commit()
    return redirect(url_for('main.show_post', post_id=replied_comment.post_id) + '#comments')


@user_bp.route('/personal/<username>')
def user_info(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    pagination = Post.query.with_parent(user).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('user/index.html', user=user, posts=posts, pagination=pagination)


@user_bp.route('/personal/setting/profile', methods=['GET', 'POST'])
@login_required
@confirm_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        db.session.commit()
        flash('资料更新成功！', 'success')
        return redirect(url_for('.user_info', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    return render_template('user/edit_profile.html', form=form)


@user_bp.route('/personal/setting/change-email', methods=['GET', 'POST'])
@fresh_login_required
@confirm_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = generate_token(user=current_user, operation=Operation.CHANGE_EMAIL, new_email=form.email.data.lower())
        send_change_email_email(to=form.email.data, user=current_user, token=token)
        flash('确认邮件已发送，请检查收件箱！', 'info')
        return redirect(url_for('.user_info', username=current_user.username))
    return render_template('user/change_email.html', form=form)


@user_bp.route('/personal/setting/change-email/<token>')
@login_required
@confirm_required
def confirm_change_email(token):
    if validate_token(user=current_user, token=token, operation=Operation.CHANGE_EMAIL):
        flash('邮箱更新成功！', 'success')
        return redirect(url_for('.user_info', username=current_user.username))
    else:
        flash('令牌错误或已超时！', 'warning')
        return redirect(url_for('.change_email'))


@user_bp.route('/personal/setting/password', methods=['GET', 'POST'])
@fresh_login_required
@confirm_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit() and current_user.validate_password(form.old_password.data):
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('密码更新成功！', 'success')
        return redirect(url_for('.user_info', username=current_user.username))
    return render_template('user/change_password.html', form=form)


@user_bp.route('/personal/setting/avatar')
@login_required
@confirm_required
def change_avatar():
    upload_form = UploadAvatarForm()
    crop_form = CropAvatarForm()
    return render_template('user/change_avatar.html', upload_form=upload_form, crop_form=crop_form)


@user_bp.route('/personal/settings/avatar/upload', methods=['POST'])
@login_required
@confirm_required
def upload_avatar():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        current_user.avatar_raw = filename
        db.session.commit()
        flash('头像上传成功，请裁剪！', 'success')
    return redirect(url_for('.change_avatar'))


@user_bp.route('/personal/avatar/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@user_bp.route('/personal/settings/avatar/crop', methods=['POST'])
@login_required
@confirm_required
def crop_avatar():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        filenames = avatars.crop_avatar(current_user.avatar_raw, x, y, w, h)
        current_user.avatar_s = filenames[0]
        current_user.avatar_m = filenames[1]
        current_user.avatar_l = filenames[2]
        db.session.commit()
        flash('裁剪头像上传成功！', 'success')
    return redirect(url_for('.change_avatar'))


@user_bp.route('/collect/<int:post_id>', methods=['POST'])
@login_required
def collect(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_collecting(post):
        flash('该文章已收藏！', 'info')
        return redirect_back()

    current_user.collect(post)
    return redirect_back()


@user_bp.route('/uncollect/<int:post_id>', methods=['POST'])
@login_required
def uncollect(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_collecting(post):
        flash('该文章未收藏！', 'info')
        return redirect_back()

    current_user.uncollect(post)
    return redirect_back()


@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash('该用户已关注！', 'info')
        return redirect_back()

    current_user.follow(user)
    return redirect_back()


@user_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        flash('未关注该用户！', 'info')
        return redirect_back()

    current_user.unfollow(user)
    return redirect_back()


@user_bp.route('/following')
@login_required
def following():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_FOLLOWING_PER_PAGE']
    pagination = current_user.following.paginate(page, per_page)
    follows = pagination.items
    # for follow in follows:
    #     print(follow.followed.followers.all())
    #     for i in follow.followed.followers.all():
    #         print(i.follower.username)
    # follow.followed.followers.all()只是查了关联表的对象
    return render_template('user/following.html', pagination=pagination, follows=follows)


@user_bp.route('/personal/<username>/comments')
@login_required
def user_comments(username):
    if current_user == User.query.filter_by(username=username).first_or_404():
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
        pagination = Comment.query.with_parent(current_user).order_by(Comment.timestamp.desc()).paginate(page, per_page)
        comments = pagination.items
        return render_template('user/comments.html', user=current_user, comments=comments, pagination=pagination)
    else:
        return redirect(url_for('user.user_info', username=username))


@user_bp.route('/personal/<username>/replies')
@login_required
def user_replies(username):
    if current_user == User.query.filter_by(username=username).first_or_404():
        replies = []
        self_comments = Comment.query.with_parent(current_user).all()
        for self_comment in self_comments:
            if self_comment.replies:
                replies.extend(self_comment.replies)
        if replies:
            replies.sort(key=lambda ct: ct.timestamp, reverse=True)
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
        pager_obj = SelfPagination(current_page=page, total_count=len(replies), base_url=request.path, params=request.args, per_page_count=per_page)
        index_list = replies[pager_obj.start:pager_obj.end]
        html = pager_obj.page_html()
        return render_template('user/replies.html', user=current_user, replies=replies, index_list=index_list, html=html)
    else:
        return redirect(url_for('user.user_info', username=username))


@user_bp.route('/personal/<username>/post/replies')
@login_required
def post_replies(username):
    if current_user == User.query.filter_by(username=username).first_or_404():
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
        pagination = Post.query.with_parent(current_user).paginate(page, per_page)
        posts = pagination.items
        comments = []
        for post in posts:
            latest_comment = Comment.query.with_parent(post).order_by(Comment.timestamp.desc()).first()
            page_settings = current_app.config['YOUNG_BLOG_PER_PAGE']
            nums = Comment.query.with_parent(post).count()
            latest_comment_page = 1 if nums <= page_settings else nums // page_settings
            comments.append((latest_comment, latest_comment_page))
        comments.sort(key=lambda ct: ct[0].timestamp, reverse=True)
        return render_template('user/post_replies.html', user=current_user, comments=comments, pagination=pagination)
    else:
        return redirect(url_for('user.user_info', username=username))


@user_bp.route('/collecting')
@login_required
def collecting():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['YOUNG_BLOG_PER_PAGE']
    pagination = Collect.query.with_parent(current_user).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('user/collecting.html', pagination=pagination, collects=collects)
