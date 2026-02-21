from app import db
from datetime import datetime, timedelta

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    
    is_completed = db.Column(db.Boolean, default=False)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Opsional: Jika ingin menyimpan posisi video terakhir ditonton (detik ke-berapa)
    video_timestamp = db.Column(db.Integer, default=0) 
    
    # Trial Fields
    trial_started_at = db.Column(db.DateTime, nullable=True) # Kapan trial dimulai
    trial_expires_at = db.Column(db.DateTime, nullable=True) # Kapan trial berakhir
    trial_cancelled = db.Column(db.Boolean, default=False) # Trial sudah dibatalkan
 

    def mark_complete(self):
        self.is_completed = True
        self.last_accessed = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<Progress User:{self.user_id} Lesson:{self.lesson_id} Done:{self.is_completed}>'