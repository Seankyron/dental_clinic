import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt, mail
from main.forms import RegistrationForm, LoginForm, UpdateAccountForm, ContactForm
from main.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message




posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


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
def announcement():
    return render_template('announcement.html', title='Announcement', posts=posts)

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(subject=form.subject.data,
                      sender=('{} <{}>'.format(form.name.data, form.email.data)),
                      recipients=['beargyu06@gmail.com' ],
                      body='{}'.format(form.message.data) + ' \n Email: {} \n Contact Number: {}'.format(form.email.data, form.contact_number.data))
        mail.send(msg)
        flash(f'Your message has been sent!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', title='Contact Us', form=form)

@app.route("/appointment")
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
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
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
                              user_email=current_user.email, date=selected_date_utc,
                              time=selected_time)

    db.session.add(appointment)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/appointment', methods=['GET', 'POST'])
def add_appointment():
    if current_user.is_authenticated:
        return render_template('add_appointment.html')
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