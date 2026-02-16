from app import db

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    content_type = db.Column(db.String(20)) # 'video', 'text', 'quiz'
    content_url = db.Column(db.String(255)) # URL video atau file
    text_content = db.Column(db.Text, nullable=True) # Isi materi jika tipe text
    order = db.Column(db.Integer, default=0) # Urutan pelajaran dalam topik
    
    # Media Compression fields
    compressed_video_versions = db.Column(db.JSON, nullable=True)  # Store paths untuk low/medium/high/webm
    compressed_image = db.Column(db.String(255), nullable=True)    # Path untuk compressed image
    compression_status = db.Column(db.String(20), default='pending') # pending, processing, completed, failed
    compression_metadata = db.Column(db.JSON, nullable=True)       # Store compression ratio, sizes, etc
    
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    
    # Relasi untuk melihat siapa saja yang sudah menyelesaikan lesson ini
    user_progress = db.relationship('LessonProgress', backref='lesson', lazy='dynamic')

    def __repr__(self):
        return f'<Lesson {self.title}>'