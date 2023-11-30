from flask import url_for, flash, redirect, jsonify
from main import db
from main.models import Appointment
from flask_login import current_user
import datetime

def accept_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.action = "ACCEPTED"
    db.session.commit()

def reject_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.action = "REJECTED"
    appointment.action = "CANCELLED"
    db.session.commit()

def holiday_status(selected_date_utc):
    if current_user.is_authenticated:
        appointment = Appointment(user_id=current_user.id, user_name=current_user.username, 
                                  user_email='admin', user_contact='admin', status='HOLIDAY',
                                  service='NULL', date=selected_date_utc, time=datetime.time(0, 0))
        db.session.add(appointment)
        db.session.commit()


def add_appointment_to_database(selected_date_utc, selected_time, selected_service):
    appointment = Appointment(user_id=current_user.id, user_name=current_user.username,
                              user_email=current_user.email, user_contact = current_user.contact,
                              service = selected_service, date=selected_date_utc, time=selected_time)
    db.session.add(appointment)
    db.session.commit()
    flash('Your appointment has been added.', 'success')
    return redirect(url_for('main.customer_announcement'))