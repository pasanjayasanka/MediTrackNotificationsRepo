import pymysql.cursors
from flask import Flask, jsonify
import os
import boto3
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection details
DB_HOST = 'meditrack-db.cdai64ksezzi.us-east-1.rds.amazonaws.com'
DB_USER = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = 'meditrack'

sender_email = "pasan.20241215@iit.ac.lk"

# Initialize boto3 SES client
ses_client = boto3.client('ses', region_name='us-east-1')  # Replace with your region

# Function to get a database connection
def get_db_connection():
    return pymysql.connect(host=DB_HOST,
                           user=DB_USER,
                           password=DB_PASSWORD,
                           db=DB_NAME,
                           port=3306,
                           cursorclass=pymysql.cursors.DictCursor)

# Function to get tomorrow's date with full time (set to start of the day and end of the day)
def get_tomorrow_date_range():
    tomorrow_start = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_end = tomorrow_start.replace(hour=23, minute=59, second=59, microsecond=999999)
    return tomorrow_start.strftime('%Y-%m-%d %H:%M:%S'), tomorrow_end.strftime('%Y-%m-%d %H:%M:%S')

# Function to send email
def send_appointment_email(doctor_name, date, recipient_email):
    subject = "Appointment Reminder"
    body = f"""
    You have Successfully booked your appointment, and below are the details of your appointment tommorrow

    Doctor Name : {doctor_name}
    Date : {date}
    """

    try:
        # Send the email
        response = ses_client.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )
        print(f"Email sent successfully to {recipient_email}! Response:", response)
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {str(e)}")

# GET route to send appointment emails for tomorrow
@app.route('/notifications', methods=['GET'])
def send_notifications():
    tomorrow_start, tomorrow_end = get_tomorrow_date_range()
    conn = get_db_connection()

    with conn.cursor() as cursor:
        # Get appointments scheduled for tomorrow
        cursor.execute(
            "SELECT email, doctor_name, appointment_date FROM appointments WHERE appointment_date BETWEEN %s AND %s",
            (tomorrow_start, tomorrow_end)
        )
        appointments = cursor.fetchall()

        if not appointments:
            conn.close()
            return jsonify({"message": "No appointments for tomorrow"}), 200

        # Send emails for each appointment
        for appointment in appointments:
            send_appointment_email(appointment['doctor_name'], appointment['appointment_date'], appointment['email'])

    conn.close()
    return jsonify({"message": "Notification emails sent successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
