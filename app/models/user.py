from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Tabel Asosiasi untuk Enrolment (Siswa mengambil Kursus)
enrollments = db.Table('enrollments',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('enrolled_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='student') # 'student', 'teacher', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relasi
    # Menggunakan string 'Course' untuk menghindari circular import
    courses_teaching = db.relationship('Course', backref='instructor', lazy='dynamic')
    enrolled_courses = db.relationship('Course', secondary=enrollments, 
                                     backref=db.backref('students', lazy='dynamic'), lazy='dynamic')
    
    # Relasi ke progress belajar
    progress = db.relationship('LessonProgress', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'