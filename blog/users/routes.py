from flask import (Blueprint, render_template, url_for, flash, redirect,
                   request, current_app, jsonify)
from flask_login import login_user, logout_user, current_user, login_required
from blog import db, bcrypt, limiter
from blog.models import User, Post
from blog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                              RequestResetForm, ResetPasswordForm)
from blog.users.utils import save_picture, generate_passwd, send_reset_email
from blog.manageUserPasswd.manager import encrypt, decrypt
from pathlib import Path
import json, os

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
@limiter.exempt
def register():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():

        # Store encrypted user data in JSON file for login
        data = encrypt(form.email.data, form.password.data)

        json_file_path = Path(current_app.root_path) / 'manageUserPasswd' / 'users.json'

        if not os.path.exists(json_file_path):
            return "JSON file not found", 404
        

        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)

        json_data = {'email': data[0], 'passwd': data[1]}

        existing_data['users'].append(json_data)

        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

        # Store user credentials in database
        hashed_passwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, passwd=hashed_passwd)

        db.session.add(user)
        db.session.commit()

        flash(f"Account created successfully for {form.username.data}! You may login now!", 'success')
        return redirect(url_for('users.login'))
    
    return render_template("register.html", title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.passwd, form.current_password.data):

            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            flash("You have been successfully logged in!", 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
            
        else:
            flash("Login unsuccessful! Invalid email and password!", 'danger')
    
    return render_template("login.html", title='Login', form=form)


@users.app_errorhandler(429)
def ratelimit_handler(e):

    flash(f"Too many attempts, please try again later!", 'danger')
    return redirect(url_for('main.home'))


@users.route("/logout")
def logout():

    logout_user()
    return redirect(url_for('users.login'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
@limiter.exempt
def account():

    image_file = url_for('static', filename='profile/' + (current_user.image_file or 'default.jpg'))

    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()

        flash("Account updated successfully!", 'success')
        return redirect(url_for('users.account'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("account.html", title="Account", image_file=image_file, form=form)


@users.route("/generate_passwd")
@limiter.exempt
def generate():

    generated_passwd = generate_passwd()

    return jsonify({'password': generated_passwd})



@users.route("/user/<string:username>")
@limiter.exempt
def user_posts(username):

    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date.desc())\
                                .paginate(page=page, per_page=5)
    
    return render_template('user_posts.html', posts=posts, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
@limiter.exempt
def reset_request():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        send_reset_email(user)

        flash("An email for password reset has been sent to you!", 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
@limiter.exempt
def reset_token(token):

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    user = User.verify_reset_token(token)

    if user is None:

        flash('That token is either invalid or expired!', 'warning')
        return redirect(url_for('users.reset_request'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():

        # Store encrypted user data in JSON file for login
        data = encrypt(user.email, form.password.data)

        json_file_path = Path(current_app.root_path) / 'manageUserPasswd' / 'users.json'

        if not os.path.exists(json_file_path):
            return "JSON file not found", 404
        

        with open(json_file_path, 'r') as json_file:
            existing_data = json.load(json_file)

        
        existing_data['users'] = [backup_user for backup_user in existing_data['users']\
                                  if decrypt(backup_user['email']) != user.email]

        json_data = {'email': data[0], 'passwd': data[1]}
        existing_data['users'].append(json_data)

        
        with open(json_file_path, 'w') as json_file:
            json.dump(existing_data, json_file, indent=4)

        # Store user credentials in database
        hashed_passwd = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.passwd = hashed_passwd

        db.session.commit()

        flash(f"Your password has been updated! You may login now!", 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='Reset Password', form=form)
