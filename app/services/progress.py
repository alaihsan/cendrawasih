from app import db
from app.models.progress import LessonProgress
from app.models.lesson import Lesson
from datetime import datetime

class ProgressService:
    """Service layer for tracking user progress"""

    @staticmethod
    def track_lesson_progress(user_id, lesson_id, is_completed=False, video_timestamp=0):
        """Track or update lesson progress for a user"""
        
        # Check if progress record exists
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        
        if progress:
            # Update existing progress
            progress.is_completed = is_completed
            progress.video_timestamp = video_timestamp
            progress.last_accessed = datetime.utcnow()
        else:
            # Create new progress record
            progress = LessonProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                is_completed=is_completed,
                video_timestamp=video_timestamp
            )
            db.session.add(progress)
        
        try:
            db.session.commit()
            return progress, "Progress berhasil disimpan"
        except Exception as e:
            db.session.rollback()
            return None, f"Error: {str(e)}"

    @staticmethod
    def mark_lesson_complete(user_id, lesson_id):
        """Mark a lesson as completed"""
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        
        if not progress:
            progress = LessonProgress(user_id=user_id, lesson_id=lesson_id, is_completed=True)
            db.session.add(progress)
        else:
            progress.is_completed = True
            progress.last_accessed = datetime.utcnow()
        
        try:
            db.session.commit()
            return True, "Pembelajaran berhasil diselesaikan"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_user_progress(user_id, course_id):
        """Get user's progress in a course"""
        from app.models.course import Course, Topic
        
        course = Course.query.get(course_id)
        if not course:
            return None, "Kursus tidak ditemukan"
        
        topics = Topic.query.filter_by(course_id=course_id).all()
        
        progress_data = {
            'course_id': course_id,
            'total_lessons': 0,
            'completed_lessons': 0,
            'progress_percent': 0,
            'topics': []
        }
        
        for topic in topics:
            lessons = Lesson.query.filter_by(topic_id=topic.id).all()
            topic_data = {
                'topic_id': topic.id,
                'topic_title': topic.title,
                'total': len(lessons),
                'completed': 0,
                'lessons': []
            }
            
            for lesson in lessons:
                progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson.id).first()
                is_completed = progress.is_completed if progress else False
                
                topic_data['lessons'].append({
                    'lesson_id': lesson.id,
                    'lesson_title': lesson.title,
                    'completed': is_completed
                })
                
                progress_data['total_lessons'] += 1
                topic_data['completed'] += 1 if is_completed else 0
                if is_completed:
                    progress_data['completed_lessons'] += 1
            
            progress_data['topics'].append(topic_data)
        
        if progress_data['total_lessons'] > 0:
            progress_data['progress_percent'] = round(
                (progress_data['completed_lessons'] / progress_data['total_lessons']) * 100
            )
        
        return progress_data, "Progress berhasil diambil"

    @staticmethod
    def get_lesson_progress(user_id, lesson_id):
        """Get specific lesson progress for a user"""
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        
        if not progress:
            return None, "Progress tidak ditemukan"
        
        return progress, "Progress berhasil diambil"

    @staticmethod
    def update_video_timestamp(user_id, lesson_id, timestamp):
        """Update the video watch timestamp"""
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        
        if not progress:
            progress = LessonProgress(user_id=user_id, lesson_id=lesson_id, video_timestamp=timestamp)
            db.session.add(progress)
        else:
            progress.video_timestamp = timestamp
            progress.last_accessed = datetime.utcnow()
        
        try:
            db.session.commit()
            return True, "Timestamp berhasil disimpan"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_course_completion_percent(user_id, course_id):
        """Get completion percentage for a course"""
        from app.models.course import Course, Topic
        
        course = Course.query.get(course_id)
        if not course:
            return 0
        
        topics = Topic.query.filter_by(course_id=course_id).all()
        total_lessons = 0
        completed_lessons = 0
        
        for topic in topics:
            lessons = Lesson.query.filter_by(topic_id=topic.id).all()
            total_lessons += len(lessons)
            
            for lesson in lessons:
                progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson.id).first()
                if progress and progress.is_completed:
                    completed_lessons += 1
        
        if total_lessons == 0:
            return 0
        
        return round((completed_lessons / total_lessons) * 100)

    @staticmethod
    def get_user_completed_courses(user_id):
        """Get all courses completed by user"""
        from app.models.course import Course, Topic
        
        # Get all enrolled courses
        from app.models.user import User
        user = User.query.get(user_id)
        
        if not user:
            return []
        
        enrolled_courses = user.enrolled_courses.all()
        completed_courses = []
        
        for course in enrolled_courses:
            completion_percent = ProgressService.get_course_completion_percent(user_id, course.id)
            if completion_percent == 100:
                completed_courses.append(course)
        
        return completed_courses

    @staticmethod
    def reset_lesson_progress(user_id, lesson_id):
        """Reset progress for a lesson"""
        progress = LessonProgress.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
        
        if progress:
            db.session.delete(progress)
            try:
                db.session.commit()
                return True, "Progress berhasil direset"
            except Exception as e:
                db.session.rollback()
                return False, f"Error: {str(e)}"
        
        return False, "Progress tidak ditemukan"
