#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install flask flask_sqlalchemy


# In[2]:


from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doctors.db'
db = SQLAlchemy(app)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    specialty = db.Column(db.String(50), nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_name = db.Column(db.String(100), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)

db.create_all()


# In[3]:


@app.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([{'id': doc.id, 'name': doc.name, 'specialty': doc.specialty} for doc in doctors])

@app.route('/doctors/<int:doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    return jsonify({'id': doctor.id, 'name': doctor.name, 'specialty': doctor.specialty})

@app.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
def get_availability(doctor_id):
    # For simplicity, assume all doctors are available from 5 PM to 9 PM, Monday to Saturday
    # and can handle 4 appointments each evening.
    now = datetime.now()
    start_of_week = now - timedelta(days=now.weekday())  # Monday
    availability = []
    for i in range(6):  # Monday to Saturday
        date = start_of_week + timedelta(days=i)
        evening_slots = [date.replace(hour=17 + j, minute=0) for j in range(4)]
        availability.append({date.strftime('%Y-%m-%d'): evening_slots})
    return jsonify(availability)

@app.route('/doctors/<int:doctor_id>/appointments', methods=['POST'])
def book_appointment(doctor_id):
    data = request.json
    appointment = Appointment(
        doctor_id=doctor_id,
        patient_name=data['patient_name'],
        appointment_time=datetime.strptime(data['appointment_time'], '%Y-%m-%dT%H:%M')
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({'id': appointment.id, 'patient_name': appointment.patient_name, 'appointment_time': appointment.appointment_time}), 201


# In[ ]:




