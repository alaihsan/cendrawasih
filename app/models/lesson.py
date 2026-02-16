from app import db

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content_type = db.Column(db.String(20)) # 'video', 'text', 'quiz'
    content_url = db.Column(db.String(255)) # URL video atau file
    text_content = db.Column(db.Text, nullable=True) # Isi materi jika tipe text
    order = db.Column(db.Integer, default=0) # Urutan pelajaran dalam topik
    
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    
    # Relasi untuk melihat siapa saja yang sudah menyelesaikan lesson ini
    user_progress = db.relationship('LessonProgress', backref='lesson', lazy='dynamic')

    def __repr__(self):
        return f'<Lesson {self.title}>'