from flask import url_for, flash, redirect, current_app, render_template
from main import db
from main.models import Appointment, Holiday, Post
from flask_login import current_user
from main.users.utils import send_email

def send_email_accept(id):
    appointment = Appointment.query.filter(Appointment.id == id).first()
    #SELECT * FROM Appointment WHERE id = {id} LIMIT 1;
    send_email('[Smile Plaza] Booked Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[appointment.user_email],
               text_body=render_template('email/appointment_status_accepted.txt',
                                         appointment=appointment))
    
def send_email_reject(id):
    appointment = Appointment.query.filter(Appointment.id == id).first()
    #SELECT * FROM Appointment WHERE id = {id} LIMIT 1;
    send_email('[Smile Plaza] Booked Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[appointment.user_email],
               text_body=render_template('email/appointment_status_rejected.txt',
                                         appointment=appointment))
    
def send_email_cancel(id):
    appointment = Appointment.query.filter(Appointment.id == id).first()
    #SELECT * FROM Appointment WHERE id = {id} LIMIT 1;
    send_email('[Smile Plaza] Booked Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[appointment.user_email],
               text_body=render_template('email/appointment_status_cancelled.txt',
                                         appointment=appointment))

def send_email_received(id):
    appointment = Appointment.query.filter(Appointment.id == id).first()
    #SELECT * FROM Appointment WHERE id = {id} LIMIT 1;
    send_email('[Smile Plaza] Booked Appointment',
               sender=current_app.config['ADMINS'][0],
               recipients=[appointment.user_email],
               text_body=render_template('email/appointment_status_pending.txt',
                                         appointment=appointment))
    
def accept_action(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    #SELECT * FROM Appointment WHERE id = {appointmentID} LIMIT 1;
    appointment.action = "ACCEPTED"
    #UPDATE Appointment SET action='ACCEPTED' WHERE id={appointmentID};
    db.session.commit()

def reject_action(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    #SELECT * FROM Appointment WHERE id = {appointmentID} LIMIT 1;
    appointment.action = "REJECTED"
    appointment.status = "CANCELLED"
    #UPDATE Appointment SET action='REJECTED', status='CANCELLED' WHERE id={appointmentID};
    db.session.commit()

def cancel_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    #SELECT * FROM Appointment WHERE id = {appointmentID} LIMIT 1;
    appointment.status = "CANCELLED"
    #UPDATE Appointment SET action='REJECTED', status='CANCELLED' WHERE id={appointmentID};
    db.session.commit()

def finish_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    #SELECT * FROM Appointment WHERE id = {appointmentID} LIMIT 1;
    appointment.status = "FINISHED"
    #UPDATE Appointment SET status = 'FINISHED' WHERE id = {appointmentID};

    db.session.commit()

def holiday_status(selected_date_utc):
    if current_user.is_authenticated:
        holiday = Holiday(date=selected_date_utc, isHoliday="HOLIDAY")
        db.session.add(holiday)
        #INSERT INTO Holiday (date) VALUES ('{selected_date_utc}');
        db.session.commit()

        post = Post(title="No Clinic", content=f"No clinic for {selected_date_utc}, all appointments are cancelled.",
                    author=current_user)
        db.session.add(post)
        #INSERT INTO Post (title, content, author_id) VALUES ('No Clinic', CONCAT('No clinic for ' , '{selected_date_utc}', ', all appointments are cancelled.'), {current_user_id});
        db.session.commit()

        appointments = Appointment.query.filter(Appointment.date == selected_date_utc).all()
        #SELECT * FROM Appointment WHERE date = '{selected_date_utc}';
        print(f"Appointment: {appointments}")
        for appointment in appointments:
            appointment.action = "REJECTED"
            appointment.status = "CANCELLED"
            #UPDATE Appointment SET action = 'REJECTED', status = 'CANCELLED' WHERE date = '{selected_date_utc}';
            db.session.commit()
            send_email_cancel(appointment.id)


def add_appointment_to_database(selected_date_utc, selected_time, selected_service):
    appointment = Appointment(user_id=current_user.id, user_name=current_user.username,
                              user_email=current_user.email, user_contact = current_user.contact,
                              service = selected_service, date=selected_date_utc, time=selected_time)
    db.session.add(appointment)
    '''
    INSERT INTO Appointment (user_id, user_name, user_email, user_contact, service, date, time)
    VALUES ('{current_user_id}', '{current_user_username}', '{current_user_email}', '{current_user_contact}', 
    '{selected_service}', '{selected_date_utc}', '{selected_time}');
    '''
    db.session.commit()
    flash('Your appointment has been added.', 'success')
    return redirect(url_for('main.customer_announcement'))