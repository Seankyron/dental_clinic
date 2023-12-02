from flask import url_for, flash, redirect, jsonify
from main import db
from main.models import Appointment, Holiday, Post
from flask_login import current_user
from main.users.utils import send_email_cancel

def accept_action(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.action = "ACCEPTED"
    db.session.commit()

def reject_action(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.action = "REJECTED"
    appointment.status = "CANCELLED"
    db.session.commit()

def cancel_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.status = "CANCELLED"
    db.session.commit()

def finish_status(appointmentID):
    appointment = Appointment.query.filter(Appointment.id == appointmentID).first()
    appointment.status = "FINISHED"
    db.session.commit()

def holiday_status(selected_date_utc):
    if current_user.is_authenticated:
        holiday = Holiday(date=selected_date_utc)
        db.session.add(holiday)
        db.session.commit()

        post = Post(title="No Clinic", content=f"No clinic for {selected_date_utc}, all appointments are cancelled.",
                    author=current_user)
        db.session.add(post)
        db.session.commit()

        appointments = Appointment.query.filter(Appointment.date == selected_date_utc).all()
        print(f"Appointment: {appointments}")
        for appointment in appointments:
            appointment.action = "REJECTED"
            appointment.status = "CANCELLED"
            db.session.commit()
            send_email_cancel(appointment.id)


def add_appointment_to_database(selected_date_utc, selected_time, selected_service):
    appointment = Appointment(user_id=current_user.id, user_name=current_user.username,
                              user_email=current_user.email, user_contact = current_user.contact,
                              service = selected_service, date=selected_date_utc, time=selected_time)
    db.session.add(appointment)
    db.session.commit()
    flash('Your appointment has been added.', 'success')
    return redirect(url_for('main.customer_announcement'))