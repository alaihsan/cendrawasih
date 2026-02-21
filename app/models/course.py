from app import db
from datetime import datetime, timedelta

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='General') # Kategori: Programming, Design, Business, Data Science, Mathematics, Languages
    grade_level = db.Column(db.String(50)) # Misal: "Kelas 7-9 SMP"
    icon_class = db.Column(db.String(50)) # Untuk FontAwesome
    color_theme = db.Column(db.String(50)) # Untuk Tailwind
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Trial Fields
    is_trial_enabled = db.Column(db.Boolean, default=True) # Apakah trial tersedia
    trial_days = db.Column(db.Integer, default=7) # Durasi trial dalam hari
    can_cancel_anytime = db.Column(db.Boolean, default=True) # Bisa batalkan trial kapan saja
    
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