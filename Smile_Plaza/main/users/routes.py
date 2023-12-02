from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from main import db, bcrypt, mail
from main.models import User, Post
from main.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, ContactForm,
                                   ResetPasswordRequestForm, ResetPasswordForm)
from main.users.utils import save_picture, send_password_reset_email
from flask_mail import Message
import os

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:  
        return redirect(url_for('users.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(FName=form.FName.data, 
                    MidName=form.MidName.data, 
                    LName=form.LName.data, 
                    gender=form.gender.data,
                    birthday=form.birthday.data, 
                    age=form.age.data, 
                    contact=form.contact.data,
                    address=form.address.data,
                    username=form.username.data, 
                    email=form.email.data, 
                    password=hashed_password)
        db.session.add(user) #INSERT INTO User VALUES: (FName, MidName, LName, gender, birthday, age, contact, address, username, email, password);
        db.session.commit() #COMMIT
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.id == 2:
            return redirect(url_for('users.admin_dashboard')) 
        else:
            return redirect(url_for('main.customer_announcement'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #SELECT * FROM users WHERE email = '{email}'
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if current_user.id == 2: #basic admin page, palitan na lang kung ano id ng pinaka admin
                return render_template('admin_dashboard.html', title='Admin Page') #palitan na lang ng admin dashboard
            else:
                return redirect(url_for('main.customer_announcement'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route("/customer_account", methods=['GET', 'POST'])
@login_required
def customer_account():
    form = UpdateAccountForm() 
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.contact = form.contact.data
        db.session.commit() 
        '''UPDATE Users
        SET image_file = picture_file, username = form.username.data, email = form.email.data, contact = form.contact.data
        WHERE CustomerID = current_user.id;
        COMMIT;'''
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.customer_account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.contact.data = current_user.contact
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('customer_account.html', title='Account',
                           image_file=image_file, form=form)

@users.route("/admin_account", methods=['GET', 'POST'])
@login_required
def admin_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.contact = form.contact.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.admin_account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.contact.data = current_user.contact
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('admin_account.html', title='Account',
                           image_file=image_file, form=form)

@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('users.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        '''UPDATE Users
        SET password = hashed_password
        WHERE CustomerID = current_user.id;
        COMMIT;'''
        flash('Your password has been reset.')
        return redirect(url_for('users.login'))
    return render_template('reset_password.html', form=form)

@users.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() #SELECT * FROM Users WHERE email = form.email.data
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('users.login'))
        else:
             flash('No email found.')
             return redirect(url_for('users.reset_password_request'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@users.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(subject=form.subject.data,
                      sender=('{} <{}>'.format(form.name.data, form.email.data)),
                      recipients= os.environ.get('EMAIL_USER'),
                      body='{}'.format(form.message.data) 
                      + ' \n Email: {} \n Contact Number: {}'.format(form.email.data, form.contact_number.data))
        mail.send(msg)
        flash(f'Your message has been sent!', 'success')
        return redirect(url_for('users.contact'))
    return render_template('contact.html', title='Contact Us', form=form)

@users.route("/customer_home")
@login_required
def customer_home():
    return render_template('customer_home.html', title='Customer Home Page')

@users.route("/admin_dashboard")
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Admin Dashboard')

@users.route("/appointment_admin")
@login_required
def appointment_admin():
    return render_template('appointment_admin.html', title='Appointment')

