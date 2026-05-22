from flask import Blueprint, request, jsonify
from database import get_connection

course_bp = Blueprint('courses', __name__)

@course_bp.route('/courses', methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        try:
            data = request.json
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO courses (course_name, course_code, total_classes) VALUES (%s, %s, %s)",
                (data['course_name'], data['course_code'], data['total_classes'])
            )
            conn.commit()
            conn.close()
            return jsonify({'message': 'Course added successfully'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()
            conn.close()
            return jsonify(courses), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@course_bp.route('/courses/<int:course_id>', methods=['GET', 'DELETE'])
def course(course_id):
    if request.method == 'DELETE':
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM attendance WHERE course_id = %s",
                (course_id,)
            )
            cursor.execute(
                "DELETE FROM courses WHERE id = %s",
                (course_id,)
            )
            conn.commit()
            conn.close()
            return jsonify({'message': 'Course deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM courses WHERE id = %s",
                (course_id,)
            )
            course = cursor.fetchone()
            conn.close()
            return jsonify(course), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500