from flask import Blueprint, request, jsonify
from database import get_connection

student_bp = Blueprint('students', __name__)

@student_bp.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        try:
            data = request.json
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO students (name, email, phone, roll_number) VALUES (%s, %s, %s, %s)",
                (data['name'], data['email'], data['phone'], data['roll_number'])
            )
            conn.commit()
            conn.close()
            return jsonify({'message': 'Student added successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            conn.close()
            return jsonify(students), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@student_bp.route('/students/<int:student_id>', methods=['GET', 'DELETE'])
def student(student_id):
    if request.method == 'DELETE':
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM attendance WHERE student_id = %s",
                (student_id,)
            )
            cursor.execute(
                "DELETE FROM students WHERE id = %s",
                (student_id,)
            )
            conn.commit()
            conn.close()
            return jsonify({'message': 'Student deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM students WHERE id = %s",
                (student_id,)
            )
            student = cursor.fetchone()
            conn.close()
            return jsonify(student), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500