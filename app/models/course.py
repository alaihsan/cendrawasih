from app import db
from datetime import datetime

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    grade_level = db.Column(db.String(50)) # Misal: "Kelas 7-9 SMP"
    icon_class = db.Column(db.String(50)) # Untuk FontAwesome
    color_theme = db.Column(db.String(50)) # Untuk Tailwind
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relasi ke materi (Topic)
    topics = db.relationship('Topic', backref='course', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Course {self.title}>'

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140)) # Misal: "Aljabar Dasar"
    order = db.Column(db.Integer) # Urutan materi dalam kursus
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    
    # Relasi ke Lesson
    lessons = db.relationship('Lesson', backref='topic', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Topic {self.title}>'