import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from main import app, db, bcrypt, mail
from main.forms import (RegistrationForm, LoginForm, UpdateAccountForm, ContactForm,
                             PostForm, ResetPasswordRequestForm, ResetPasswordForm)
from main.models import User, Post, Appointment
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from datetime import datetime
import pytz

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/treatment")
def treatment():
    return render_template('treatment.html', title='Treatments')

@app.route("/announcement")
@login_required
def announcement():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('announcement.html', title='Announcement', posts=posts)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(subject=form.subject.data,
                      sender=('{} <{}>'.format(form.name.data, form.email.data)),
                      recipients=['beargyu06@gmail.com' ],
                      body='{}'.format(form.message.data) 
                      + ' \n Email: {} \n Contact Number: {}'.format(form.email.data, form.contact_number.data))
        mail.send(msg)
        flash(f'Your message has been sent!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', title='Contact Us', form=form)

@app.route("/appointment")
@login_required
def appointment():
    return render_template('appointment.html', title='Appointment')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(FName=form.FName.data, MidName=form.MidName.data, LName=form.LName.data, gender=form.gender.data,
                    birthday=form.birthday.data, age=form.age.data, contact=form.contact.data,address=form.address.data,
                     username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            if current_user.id == 3: #basic admin page, palitan na lang kung ano id ng pinaka admin
                return render_template('admin_dashboard.html', title='Admin Page') #palitan na lang ng admin dashboard
            else:
                return redirect(url_for('announcement'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.contact.data = current_user.contact
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

def add_appointment_to_database(selected_date_utc, selected_time, selected_service):
    appointment = Appointment(user_id=current_user.id, user_name=current_user.username,
                              user_email=current_user.email, service = selected_service,
                              date=selected_date_utc, time=selected_time)

    db.session.add(appointment)
    db.session.commit()
    flash(f'Your appointment has been added.')
    return redirect(url_for('home'))

@app.route('/appointment', methods=['GET', 'POST'])
@login_required
def add_appointment():
    if current_user.is_authenticated:
        return render_template('add_appointment.html', title='Appointment')
    else:
        return redirect(url_for('register'))


@app.route('/get_available_times', methods=['POST'])
def get_available_times():
    if request.method == 'POST':
        data = request.get_json()
        selected_date = data.get('selectedDate')

        print(f"Received request for date: {selected_date}")

        selected_date_utc = datetime.fromisoformat(selected_date.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC).date()

        occupied_times = [time[0].strftime('%I:%M %p') for time in
                           Appointment.query.filter_by(date=selected_date_utc).with_entities(Appointment.time).all()]
        all_time_slots = ['08:00 AM', '08:30 AM', '09:00 AM', '09:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM',
                          '01:00 PM', '01:30 PM', '02:00 PM', '03:00 PM']
        available_time_slots = [time for time in all_time_slots if time not in occupied_times]

        print(f"Occupied times for {selected_date_utc}: {occupied_times}")
        print(f"Available times for {selected_date_utc}: {available_time_slots}")

        return jsonify({'availableTimes': available_time_slots})

    return jsonify({'message': 'Invalid request'}), 400

@app.route('/get_appointment', methods=['POST'])
def get_appointment():
    if request.method == 'POST':
        data = request.get_json()
        selected_date = data.get('selectedDate')
        print(f"Selected Date: {selected_date}")
        selected_date_utc = datetime.fromisoformat(selected_date.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC).date()
        selected_slot = data.get('selectedSlot')
        selected_time = datetime.strptime(selected_slot, '%I:%M %p').time()
        selected_service = data.get('selectedService')

        print(f"Selected Date: {selected_date_utc}, Selected time slot: {selected_slot}, Selected service: {selected_service}")
        add_appointment_to_database(selected_date_utc, selected_time, selected_service)

        # You can return a response to the frontend if needed
        return jsonify({'message': 'Data received successfully'})

    return jsonify({'message': 'Invalid request'}), 400

@app.route("/appointment_admin")
@login_required
def appointment_admin():
    appointments = Appointment.query.all()
    return render_template('appointment_admin.html', title='Appointment')

@app.route("/customer_home")
@login_required
def customer_home():
    return render_template('customer_home.html', title='Customer Home Page')

@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Admin Dashboard')

@app.route("/new_post", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('announcement'))
    return render_template('new_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('announcement'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token))

def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    mail.send(msg)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)