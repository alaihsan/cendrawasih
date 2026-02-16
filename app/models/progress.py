from app import db
from datetime import datetime

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    
    is_completed = db.Column(db.Boolean, default=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Opsional: Jika ingin menyimpan posisi video terakhir ditonton (detik ke-berapa)
    video_timestamp = db.Column(db.Integer, default=0) 

    def mark_complete(self):
        self.is_completed = True
        self.last_accessed = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<Progress User:{self.user_id} Lesson:{self.lesson_id} Done:{self.is_completed}>'