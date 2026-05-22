from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "DELETE", "PUT", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

mail = Mail(app)

from routes.student_routes import student_bp
from routes.course_routes import course_bp
from routes.attendance_routes import attendance_bp

app.register_blueprint(student_bp)
app.register_blueprint(course_bp)
app.register_blueprint(attendance_bp)

if __name__ == '__main__':
    app.run(debug=True)