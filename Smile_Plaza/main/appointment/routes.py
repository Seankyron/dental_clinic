from flask import render_template, url_for, flash, redirect, request, jsonify, Blueprint
from main import db, bcrypt, mail
from main.models import User, Appointment
from flask_login import current_user, login_required
from datetime import datetime
import pytz
from sqlalchemy import desc
from main.appointment.utils import add_appointment_to_database, reject_status, accept_status, holiday_status

appointment = Blueprint('appointment', __name__)

@appointment.route('/appointment', methods=['GET', 'POST'])
@login_required
def add_appointment():
    if current_user.is_authenticated:
        return render_template('appointment.html', title='Appointment')
    else:
        return redirect(url_for('appointment.register'))


@appointment.route('/get_available_times', methods=['POST'])
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

@appointment.route('/get_appointment', methods=['POST'])
def get_appointment():
    if request.method == 'POST':
        data = request.get_json()
        selected_date = data.get('selectedDate')
        print(f"Selected Date: {selected_date}")
        selected_date_utc = datetime.fromisoformat(selected_date.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC).date()
        selected_slot = data.get('selectedSlot')
        selected_time = datetime.strptime(selected_slot, '%I:%M %p').time()
        selected_service = data.get('selectedService')

        print(f"Selected Date: {selected_date_utc}, Selected time slot: {selected_time}, Selected service: {selected_service}")
        add_appointment_to_database(selected_date_utc, selected_time, selected_service)

        # You can return a response to the frontend if needed
        return jsonify({'message': 'Data received successfully'})

    return jsonify({'message': 'Invalid request'}), 400


@appointment.route('/get_appointment_data', methods=['POST'])
def get_appointment_data():
    if request.method == 'POST':
        data = request.get_json()
        selected_date = data.get('selectedDate')

        print(f"Received request for date: {selected_date}")

        selected_date_utc = datetime.fromisoformat(selected_date.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC).date()

        appointment_info = Appointment.query.filter(Appointment.date == selected_date_utc).with_entities(
            Appointment.id, Appointment.time, Appointment.user_name, Appointment.user_email, Appointment.user_contact,
            Appointment.service, Appointment.action, Appointment.status).all()

        result = []
        for row in appointment_info:
            row_data = [row.id, row.time.strftime('%I:%M %p'), row.user_name, row.user_email, row.user_contact,
                        row.service, row.action, row.status]
            result.append(row_data)

        print(f"Appointments for {selected_date_utc}: {result}")
        return jsonify({'appointmentInfo': result})

    return jsonify({'message': 'Invalid request'}), 400

@appointment.route('/get/appointment_data_dashboard', methods=['POST'])
def get_appointment_data_dashboard():
    if request.method == 'POST':
        all_appointment = Appointment.query.with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status).all() 

        result_all = []
        for row in all_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.status]
            result_all.append(row_data)

        print(f"Appointments: {result_all}")
        
        pending_appointment = Appointment.query.filter(Appointment.action == 
                                                    "PENDING").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status).all() 

        result_pending = []
        for row in pending_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.status]
            result_pending.append(row_data)

        print(f"Appointments: {result_pending}")

        accepted_appointment = Appointment.query.filter(Appointment.action == 
                                                    "ACCEPTED").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status).all() 

        result_accepted = []
        for row in accepted_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.status]
            result_accepted.append(row_data)

        print(f"Appointments: {result_accepted}")

        rejected_appointment = Appointment.query.filter(Appointment.action == 
                                                    "REJECTED").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status).all() 

        result_rejected = []
        for row in rejected_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.status]
            result_rejected.append(row_data)

        print(f"Appointments: {result_rejected}")

        totalPatients = User.query.with_entities(User.id).order_by(desc(User.id)).first()[0]
        print(f"Total Patients: {totalPatients}")

        totalAppointments = Appointment.query.with_entities(Appointment.id).order_by(desc(Appointment.id)).first()[0]
        print(f"Total Appointments: {totalAppointments}")

        value = {'appointmentAll': result_all,
                 'appointmentPending': result_pending,
                 'appointmentAccepted': result_accepted,
                 'appointmentRejected': result_rejected,
                 'totalPatients': totalPatients,
                 'totalAppointments': totalAppointments}
        return jsonify(value)

    return jsonify({'message': 'Invalid request'}), 400

@appointment.route('/get/status', methods=['POST'])
def accept_reject():
    if request.method == 'POST':
        data = request.get_json()
        selected_appt_id = data.get('appointmentID')
        action = data.get('action')
        print(f"Selected Appointment: {selected_appt_id}, {action}")

        if(action == "ACCEPTED"):
            accept_status(selected_appt_id)
        elif(action == "REJECTED"):
            reject_status(selected_appt_id)
        else:
            selected_date = data.get('selectedDate')
            print(f"Selected Date for holiday: {selected_date}")
            selected_date_utc = datetime.fromisoformat(selected_date.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC).date()

            print(f"Selected Date for holiday: {selected_date_utc}")
            holiday_status(selected_date_utc)

        # You can return a response to the frontend if needed
        return jsonify({'message': 'Data received successfully'})

    return jsonify({'message': 'Invalid request'}), 400