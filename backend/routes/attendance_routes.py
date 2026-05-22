from flask import Blueprint, request, jsonify, current_app
from flask_mail import Mail, Message
from database import get_connection

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendance (student_id, course_id, date, status) VALUES (%s, %s, %s, %s)",
        (data['student_id'], data['course_id'], data['date'], data['status'])
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Attendance marked'}), 201

@attendance_bp.route('/attendance/percentage/<int:student_id>', methods=['GET'])
def get_percentage(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.course_name,
            COUNT(*) as total_classes,
            SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
            ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = %s
        GROUP BY a.course_id
    """, (student_id,))
    result = cursor.fetchall()
    conn.close()
    return jsonify(result), 200

@attendance_bp.route('/attendance/shortage', methods=['GET'])
def get_shortage():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.name, s.email, s.roll_number,
            c.course_name,
            ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN courses c ON a.course_id = c.id
        GROUP BY a.student_id, a.course_id
        HAVING percentage < 75
    """)
    result = cursor.fetchall()
    conn.close()
    return jsonify(result), 200

@attendance_bp.route('/attendance/send-alerts', methods=['GET'])
def send_alerts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.name, s.email,
            c.course_name,
            ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN courses c ON a.course_id = c.id
        GROUP BY a.student_id, a.course_id
        HAVING percentage < 75
    """)
    students = cursor.fetchall()
    conn.close()

    mail = Mail(current_app)
    for student in students:
        msg = Message(
            subject="Attendance Shortage Alert",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[student['email']]
        )
        msg.body = f"""
Dear {student['name']},
Your attendance in {student['course_name']} is {student['percentage']}%.
Minimum required is 75%. Please attend classes regularly.
Regards,
Attendance Management System
        """
        mail.send(msg)

    return jsonify({'message': f'Alerts sent to {len(students)} students'}), 200
# Generate Report
@attendance_bp.route('/attendance/report', methods=['GET'])
def get_report():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.name,
            s.roll_number,
            s.email,
            c.course_name,
            COUNT(*) as total_classes,
            SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
            SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
            ROUND(SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN courses c ON a.course_id = c.id
        GROUP BY a.student_id, a.course_id
        ORDER BY s.name
    """)
    result = cursor.fetchall()
    conn.close()
    return jsonify(result), 200
import pandas as pd
import os
from flask import request

@attendance_bp.route('/attendance/upload', methods=['POST'])
def upload_attendance():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            return jsonify({'error': 'Only CSV or Excel files allowed'}), 400

        conn = get_connection()
        cursor = conn.cursor()

        success_count = 0
        error_count = 0

        for _, row in df.iterrows():
            try:
                # Get student id from roll number
                cursor.execute(
                    "SELECT id FROM students WHERE roll_number = %s",
                    (str(row['roll_number']),)
                )
                student = cursor.fetchone()

                # Get course id from course code
                cursor.execute(
                    "SELECT id FROM courses WHERE course_code = %s",
                    (str(row['course_code']),)
                )
                course = cursor.fetchone()

                if student and course:
                    cursor.execute(
                        "INSERT INTO attendance (student_id, course_id, date, status) VALUES (%s, %s, %s, %s)",
                        (student['id'], course['id'], row['date'], row['status'])
                    )
                    success_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1

        conn.commit()
        conn.close()

        return jsonify({
            'message': f'Upload complete! {success_count} records added, {error_count} failed.'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500