import os
import secrets
from PIL import Image
from flask import current_app, render_template
from flask_mail import Message
from flask import current_app
from main import mail
from main.models import Appointment

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
    
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Smile Plaza] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token))

def send_email_accept(id):
    appointment = Appointment.query.filter(Appointment.id == id).first()

    send_email('[Smile Plaza] Booked Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[appointment.user_email],
               text_body=render_template('email/appointment_status_accepted.txt',
                                         appointment=appointment))
    
def send_email_reject(id):
    appointment = Appointment.query.filter(Appointment.id == id).first()
    send_email('[Smile Plaza] Booked Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[appointment.user_email],
               text_body=render_template('email/appointment_status_rejected.txt',
                                         appointment=appointment))
    
def send_email_cancel(id):
    appointment = Appointment.query.filter(Appointment.id == id).first()
    send_email('[Smile Plaza] Booked Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[appointment.user_email],
               text_body=render_template('email/appointment_status_cancelled.txt',
                                         appointment=appointment))

def send_email(subject, sender, recipients, text_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    mail.send(msg)