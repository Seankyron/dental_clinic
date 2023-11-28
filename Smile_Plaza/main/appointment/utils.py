from flask import url_for, flash, redirect, request, jsonify
from main import db, bcrypt, mail
from main.models import Appointment
from flask_login import current_user


def accept_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.status = "ACCEPTED"
    db.session.commit()

def reject_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.status = "REJECTED"
    db.session.commit()

def add_appointment_to_database(selected_date_utc, selected_time, selected_service):
    appointment = Appointment(user_id=current_user.id, user_name=current_user.username,
                              user_email=current_user.email, user_contact = current_user.contact,
                              service = selected_service, date=selected_date_utc, time=selected_time)
    db.session.add(appointment)
    db.session.commit()
    flash('Your appointment has been added.', 'success')
    return redirect(url_for('main.announcement'))