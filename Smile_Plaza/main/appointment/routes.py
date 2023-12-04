from main import db
from flask import render_template, url_for, abort, request, jsonify, Blueprint
from main.models import User, Appointment, Holiday
from flask_login import current_user, login_required
from datetime import datetime
import pytz
from sqlalchemy import desc, asc, func
from main.appointment.utils import add_appointment_to_database, reject_action, accept_action, holiday_status, finish_status, cancel_status
from main.users.utils import send_email_accept, send_email_reject, send_email_cancel

appointment = Blueprint('appointment', __name__)

@appointment.route('/appointment', methods=['GET', 'POST'])
@login_required
def add_appointment():
    if current_user.is_authenticated:
        return render_template('appointment.html', title='Appointment')
    return (url_for('users.register'))


@appointment.route("/appointment_admin")
@login_required
def appointment_admin():
    if current_user.id == 1:
        return render_template('appointment_admin.html', title='Appointment')
    else:
        abort(403)

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
        """
            SELECT id, time, user_name, user_email, user_contact, service, action, status
            FROM Appointment
            WHERE date = '{selected_date_utc}'
        """

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
                                    Appointment.date, Appointment.time, Appointment.service, 
                                    Appointment.action, Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), asc(Appointment.time)).all() 
        """
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        ORDER BY Appointment.date DESC, Appointment.time ASC
        """

        result_all = []
        for row in all_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_all.append(row_data)

        print(f"Appointments: {result_all}")

        all_patients = db.session.query(User.username, User.id, User.age, User.email, User.contact,
                            User.address, func.count(Appointment.id).label('appointment_count')).outerjoin(Appointment,
                            User.id == Appointment.user_id).group_by(User.id).all()
        '''
        SELECT u.username, u.id, u.age, u.email, u.contact, u.address, COUNT(a.id) AS appointment_count
        FROM User u
        LEFT OUTER JOIN Appointment a ON u.id = a.user_id
        GROUP BY u.id;
        '''
        
        result_patients = []
        for row in all_patients:
            row_data = [row.id, row.username, row.age, row.email, row.contact, row.address, row.appointment_count]
            result_patients.append(row_data)
        
        patient_appointment = Appointment.query.with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(asc(Appointment.user_id), 
                                                                                                          desc(Appointment.date), asc(Appointment.time)).all() 
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        ORDER BY Appointment.user_id ASC, Appointment.date DESC, Appointment.time ASC
        '''

        result_patient_appointment = []
        for row in patient_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_patient_appointment.append(row_data)

        pending_appointment = Appointment.query.filter(Appointment.action == 
                                                    "PENDING").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), 
                                                                                                          asc(Appointment.time)).all() 
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        WHERE action = 'PENDING'
        ORDER BY Appointment.date DESC, Appointment.time ASC;
        '''

        result_pending = []
        for row in pending_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_pending.append(row_data)

        print(f"Appointments: {result_pending}")

        accepted_appointment = Appointment.query.filter(Appointment.action == 
                                                    "ACCEPTED").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), 
                                                                                                          asc(Appointment.time)).all() 
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        WHERE action = 'ACCEPTED'
        ORDER BY Appointment.date DESC, Appointment.time ASC;
        '''

        result_accepted = []
        for row in accepted_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_accepted.append(row_data)

        print(f"Appointments: {result_accepted}")

        rejected_appointment = Appointment.query.filter(Appointment.action == 
                                                    "REJECTED").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), 
                                                                                                          asc(Appointment.time)).all() 
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        WHERE action = 'REJECTED'
        ORDER BY Appointment.date DESC, Appointment.time ASC;
        '''

        result_rejected = []
        for row in rejected_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_rejected.append(row_data)

        print(f"Appointments: {result_rejected}")
        
        not_finished_appointment = Appointment.query.filter(Appointment.status == 
                                                    "NOT FINISHED").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), 
                                                                                                          asc(Appointment.time)).all()
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        WHERE appointment.status = 'NOT FINISHED'
        ORDER BY Appointment.date DESC, Appointment.time ASC;
        ''' 

        result_not_finished = []
        for row in not_finished_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_not_finished.append(row_data)

        print(f"Appointments: {result_not_finished}")
        
        finished_appointment = Appointment.query.filter(Appointment.status == 
                                                    "FINISHED").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), 
                                                                                                          asc(Appointment.time)).all() 
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        WHERE appointment.status = 'FINISHED'
        ORDER BY Appointment.date DESC, Appointment.time ASC;
        '''

        result_finished = []
        for row in finished_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_finished.append(row_data)

        cancelled_appointment = Appointment.query.filter(Appointment.status == 
                                                    "CANCELLED").with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), 
                                                                                          asc(Appointment.time)).all() 
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        WHERE Appointment.status = 'CANCELLED'
        ORDER BY Appointment.date DESC, Appointment.time ASC;
        '''

        result_cancelled = []
        for row in cancelled_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_cancelled.append(row_data)

        user_appointment = Appointment.query.filter(Appointment.user_name == 
                                                    current_user.username).with_entities(Appointment.id, Appointment.user_name,
                                                        Appointment.date, Appointment.time, 
                                                        Appointment.service, Appointment.action,
                                                        Appointment.status, Appointment.user_id).order_by(desc(Appointment.date), 
                                                                                                          asc(Appointment.time)).all()
        '''
        SELECT Appointment.id, Appointment.user_name, Appointment.date, Appointment.time, 
        Appointment.service, Appointment.action, Appointment.status, Appointment.user_id
        FROM Appointment
        WHERE Appointment.user_name = current_user.username
        ORDER BY Appointment.date DESC, Appointment.time ASC;
        ''' 

        result_user = []
        for row in user_appointment:
            row_data = [row.id, row.user_name, row.date.strftime('%m/%d/%Y'),
                        row.time.strftime('%I:%M %p'), row.service, row.action, 
                        row.status, row.user_id]
            result_user.append(row_data)

        print(f"Your appointments: ", result_user)

        totalPatients = User.query.with_entities(User.id).order_by(desc(User.id)).first()[0] - 1
        #SELECT id - 1 AS TotalPatients FROM User ORDER BY id DESC LIMIT 1;
        print(f"Total Patients: {totalPatients-1}") #admin is not included


        pendingAppointments = Appointment.query.filter(Appointment.action == "PENDING").count()
        print(f"Pending Appointments: {pendingAppointments}")
        #SELECT COUNT(*) FROM Appointment WHERE action = 'PENDING';


        notFinishedAppointments = Appointment.query.filter(Appointment.status == "NOT FINISHED").count()
        print(f"Not Finished Appointments: {notFinishedAppointments}")
        #SELECT COUNT(*) FROM Appointment WHERE status = 'NOT FINISHED';


        value = {'appointmentAll': result_all,
                 'patientAll': result_patients,
                 'appointmentPatient': result_patient_appointment,
                 'appointmentPending': result_pending,
                 'appointmentAccepted': result_accepted,
                 'appointmentRejected': result_rejected,
                 'appointmentNotFinished': result_not_finished,
                 'appointmentFinished': result_finished,
                 'appointmentCancelled': result_cancelled,
                 'totalPatients': totalPatients,
                 'pendingAppointments': pendingAppointments,
                 'notFinishedAppointments' : notFinishedAppointments,
                 'userAppointments': result_user}
        return jsonify(value)

    return jsonify({'message': 'Invalid request'}), 400

@appointment.route('/get/action', methods=['POST'])
def accept_reject():
    if request.method == 'POST':
        data = request.get_json()
        selected_appt_id = data.get('appointmentID')
        action = data.get('action')
        print(f"Selected Appointment: {selected_appt_id}, {action}")

        if(action == "ACCEPTED"):
            accept_action(selected_appt_id)
            send_email_accept(selected_appt_id)
        elif(action == "REJECTED"):
            reject_action(selected_appt_id)
            send_email_reject(selected_appt_id)
        else:
            selected_date = data.get('selectedDate')
            print(f"Selected Date for holiday: {selected_date}")
            selected_date_utc = datetime.fromisoformat(selected_date.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC).date()

            print(f"Selected Date for holiday: {selected_date_utc}")
            holiday_status(selected_date_utc)

        # You can return a response to the frontend if needed
        return jsonify({'message': 'Data received successfully'})

    return jsonify({'message': 'Invalid request'}), 400

@appointment.route('/get/status', methods=['POST'])
def finish_cancel():
    if request.method == 'POST':
        data = request.get_json()
        selected_appt_id = data.get('appointmentID')
        status = data.get('status')
        print(f"Selected Appointment: {selected_appt_id}, {status}")

        if(status == "FINISHED"):
            finish_status(selected_appt_id)
        else:
            cancel_status(selected_appt_id)
            send_email_cancel(selected_appt_id)

        # You can return a response to the frontend if needed
        return jsonify({'message': 'Data received successfully'})

    return jsonify({'message': 'Invalid request'}), 400

@appointment.route('/get/holidays', methods=['POST'])
def get_holidays():
    if request.method == 'POST':
        data = request.get_json()
        selected_date = data.get('selectedDate')

        print(f"Received request for date: {selected_date}")

        selected_date_utc = datetime.fromisoformat(selected_date.replace("Z", "+00:00")).replace(tzinfo=pytz.UTC).date()

        holiday = Holiday.query.filter(Holiday.date == selected_date_utc).with_entities(Holiday.date).first()
        if holiday is not None:
            result = [holiday.date]
        else:
            result = []
        """
        SELECT date
        FROM holiday
        WHERE date = 'selected_date_utc' LIMIT 1;
        """

        print('Holiday: ', holiday)
        print('Result: ', result)

        return jsonify({'holidayInfo': result})

    return jsonify({'message': 'Invalid request'}), 400
