import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, UpdateEmailForm, UpdatePasswordForm, UpdateAvatarForm, PostForm, CommentForm
from app.models import User, Post, Comment
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/", methods=['GET', 'POST'])
def home():
    form = LoginForm()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.likes.desc()).paginate(page=page, per_page=10)

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check username and password!', 'danger')
    if current_user.is_authenticated:
        avatar = url_for('static', filename='profile_pics/' + current_user.avatar)
        return render_template("home.html", posts=posts, avatar=avatar)
    else:
        return render_template("home.html", posts=posts, form=form)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('home'))
    return render_template("signup.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check username and password!', 'danger')
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    avatar = url_for('static', filename='profile_pics/' + current_user.avatar)
    return render_template('account.html', avatar=avatar)


@app.route("/account/updatemail", methods=['GET', 'POST'])
@login_required
def updatemail():
    form = UpdateEmailForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        db.session.commit()
        flash('Your e-mail has been updated!', 'success')
        return redirect(url_for('account'))
    return render_template('updatemail.html', form=form)


@app.route("/account/updatepassword", methods=['GET', 'POST'])
@login_required
def updatepassword():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.currentPassword.data):
            hashed_password = bcrypt.generate_password_hash(form.newPassword.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('account'))
        else:
            flash('Current password is incorrect', 'danger')
    return render_template('updatepassword.html', form=form)


def save_picture(form_avatar):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_avatar.filename)
    avatar_fn = random_hex + f_ext
    avatar_path = os.path.join(app.root_path, 'static/profile_pics', avatar_fn)
    output_size = (125, 125)
    i = Image.open(form_avatar)
    i.thumbnail(output_size)
    i.save(avatar_path)

    return avatar_fn


@app.route("/account/updateavatar", methods=['GET', 'POST'])
@login_required
def updateavatar():
    form = UpdateAvatarForm()
    avatar = url_for('static', filename='profile_pics/' + current_user.avatar)
    if form.validate_on_submit():
        if form.avatar.data:
            avatar_file = save_picture(form.avatar.data)
            current_user.avatar = avatar_file
            db.session.commit()
            flash('Your avatar has been updated!', 'success')
            return redirect(url_for('account'))
    return render_template('updateavatar.html', form=form, avatar=avatar)


@app.route("/createpost", methods=['GET', 'POST'])
@login_required
def createpost():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('createpost.html', title='Create Post', form=form)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def post(post_id):
    loginForm = LoginForm()
    commentForm = CommentForm()
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id)
    if loginForm.validate_on_submit():
        user = User.query.filter_by(username=loginForm.username.data).first()
        if user and bcrypt.check_password_hash(user.password, loginForm.password.data):
            login_user(user, remember=loginForm.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Check username and password!', 'danger')
    if commentForm.validate_on_submit():
        comment = Comment(content=commentForm.content.data, author=current_user, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been added!', 'success')
        return redirect(url_for('post', post_id=post.id))
    if current_user.is_authenticated:
        avatar = url_for('static', filename='profile_pics/' + current_user.avatar)
        return render_template("post.html", post=post, commentForm=commentForm, avatar=avatar, comments=comments)
    else:
        return render_template("post.html", post=post, loginForm=loginForm, comments=comments)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if request.method == 'GET':
        form.content.data = post.content
    if form.validate_on_submit():
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('createpost.html', title='Update Post', form=form)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/post/<int:post_id>/like", methods=['GET', 'POST'])
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_authenticated:
        post.likes = post.likes+1
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    else:
        flash('You need to be logged in to be able to rate the post!', 'danger')
        return redirect(url_for('post', post_id=post.id))

@app.route("/post/<int:post_id>/unlike", methods=['GET', 'POST'])
def unlike_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.is_authenticated:
        post.likes = post.likes-1
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    else:
        flash('You need to be logged in to be able to rate the post!', 'danger')
        return redirect(url_for('post', post_id=post.id))

@app.route("/post/<int:post_id>/comment/<int:comment_id>/like", methods=['GET', 'POST'])
def like_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    if current_user.is_authenticated:
        comment.likes = comment.likes+1
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    else:
        flash('You need to be logged in to be able to rate the comments!', 'danger')
        return redirect(url_for('post', post_id=post.id))

@app.route("/post/<int:post_id>/comment/<int:comment_id>/unlike", methods=['GET', 'POST'])
def unlike_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    if current_user.is_authenticated:
        comment.likes = comment.likes-1
        db.session.commit()
        return redirect(url_for('post', post_id=post.id))
    else:
        flash('You need to be logged in to be able to rate the comments!', 'danger')
        return redirect(url_for('post', post_id=post.id))

@app.route("/post/<int:post_id>/comment/<int:comment_id>/update", methods=['GET', 'POST'])
def update_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    form = PostForm()
    if request.method == 'GET':
        form.content.data = comment.content
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash('Your comment has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    return render_template('createpost.html', title='Update Comment', form=form)

@app.route("/post/<int:post_id>/comment/<int:comment_id>/delete", methods=['POST'])
def delete_comment(post_id, comment_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted!', 'success')
    return redirect(url_for('post', post_id=post.id))

@app.route("/account/delete")
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()
    flash('Your account has been deleted!', 'success')
    return redirect(url_for('logout'))

@app.route("/user/<string:username>")
def user_page(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('userpage.html', posts=posts, user=user)