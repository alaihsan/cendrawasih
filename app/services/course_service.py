from app import db
from app.models.course import Course, Topic
from app.models.lesson import Lesson
from app.models.user import enrollments
from app.models.progress import LessonProgress
from datetime import datetime, timedelta

class CourseService:
    """Service layer for course management"""

    @staticmethod
    def create_course(title, description, grade_level, instructor_id, icon_class='fa-book', color_theme='emerald'):
        """Create a new course"""
        course = Course(
            title=title,
            description=description,
            grade_level=grade_level,
            instructor_id=instructor_id,
            icon_class=icon_class,
            color_theme=color_theme
        )
        
        try:
            db.session.add(course)
            db.session.commit()
            return course, "Kursus berhasil dibuat"
        except Exception as e:
            db.session.rollback()
            return None, f"Error: {str(e)}"

    @staticmethod
    def get_course_by_id(course_id):
        """Get course by ID with relationships"""
        return Course.query.get(course_id)

    @staticmethod
    def get_all_courses():
        """Get all courses"""
        return Course.query.all()

    @staticmethod
    def get_courses_by_instructor(instructor_id):
        """Get courses by instructor ID"""
        return Course.query.filter_by(instructor_id=instructor_id).all()

    @staticmethod
    def get_user_enrolled_courses(user_id):
        """Get all courses where user is enrolled"""
        from app.models.user import User
        user = User.query.get(user_id)
        if user:
            return user.enrolled_courses.all()
        return []

    @staticmethod
    def enroll_student(user_id, course_id):
        """Enroll a student to a course"""
        from app.models.user import User
        
        user = User.query.get(user_id)
        course = Course.query.get(course_id)
        
        if not user or not course:
            return False, "User atau Course tidak ditemukan"
        
        # Check if already enrolled
        if course in user.enrolled_courses:
            return False, "Anda sudah mendaftar kursus ini"
        
        try:
            user.enrolled_courses.append(course)
            db.session.commit()
            return True, "Berhasil mendaftar kursus"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def unenroll_student(user_id, course_id):
        """Unenroll a student from a course"""
        from app.models.user import User
        
        user = User.query.get(user_id)
        course = Course.query.get(course_id)
        
        if not user or not course:
            return False, "User atau Course tidak ditemukan"
        
        try:
            user.enrolled_courses.remove(course)
            db.session.commit()
            return True, "Berhasil keluar dari kursus"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def get_course_students(course_id):
        """Get all students enrolled in a course"""
        course = Course.query.get(course_id)
        if course:
            return course.students.all()
        return []

    @staticmethod
    def is_student_enrolled(user_id, course_id):
        """Check if student is enrolled in course"""
        from app.models.user import User
        
        user = User.query.get(user_id)
        if user:
            return Course.query.filter_by(id=course_id).filter(
                Course.students.any(id=user_id)
            ).first() is not None
        return False

    # Trial methods
    @staticmethod
    def start_trial(user_id, course_id):
        """Start a trial period for a user in a course"""
        from app.models.user import User
        
        user = User.query.get(user_id)
        course = Course.query.get(course_id)
        
        if not user or not course:
            return False, "User atau Course tidak ditemukan"
        
        if not course.is_trial_enabled:
            return False, "Trial tidak tersedia untuk kursus ini"
        
        # Check if already enrolled
        if course in user.enrolled_courses:
            return False, "Anda sudah mendaftar kursus ini"
        
        try:
            # Enroll user to course with trial data
            user.enrolled_courses.append(course)
            
            # Create progress record with trial dates
            trial_started = datetime.utcnow()
            trial_expires = trial_started + timedelta(days=course.trial_days)
            
            # Get first lesson for trial tracking
            first_lesson = Lesson.query.join(Topic).filter(
                Topic.course_id == course_id
            ).order_by(Topic.order, Lesson.order).first()
            
            if first_lesson:
                progress = LessonProgress(
                    user_id=user_id,
                    lesson_id=first_lesson.id,
                    trial_started_at=trial_started,
                    trial_expires_at=trial_expires,
                    trial_cancelled=False
                )
                db.session.add(progress)
            
            db.session.commit()
            return True, f"Trial berhasil dimulai! Berlaku selama {course.trial_days} hari"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def cancel_trial(user_id, course_id):
        """Cancel trial and remove enrollment"""
        from app.models.user import User
        
        user = User.query.get(user_id)
        course = Course.query.get(course_id)
        
        if not user or not course:
            return False, "User atau Course tidak ditemukan"
        
        try:
            # Mark trial as cancelled
            progress_records = LessonProgress.query.join(Lesson).join(Topic).filter(
                Topic.course_id == course_id,
                LessonProgress.user_id == user_id,
                LessonProgress.trial_started_at.isnot(None)
            ).all()
            
            for progress in progress_records:
                progress.trial_cancelled = True
            
            # Remove enrollment
            user.enrolled_courses.remove(course)
            db.session.commit()
            return True, "Trial berhasil dibatalkan"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def is_trial_active(user_id, course_id):
        """Check if user has an active trial for a course"""
        progress = LessonProgress.query.join(Lesson).join(Topic).filter(
            Topic.course_id == course_id,
            LessonProgress.user_id == user_id,
            LessonProgress.trial_started_at.isnot(None),
            LessonProgress.trial_cancelled == False,
            LessonProgress.trial_expires_at > datetime.utcnow()
        ).first()
        
        return progress is not None

    @staticmethod
    def has_trial_access(user_id, course_id):
        """Check if user has trial OR full enrollment access"""
        # Check full enrollment
        if CourseService.is_student_enrolled(user_id, course_id):
            return True
        
        # Check active trial
        return CourseService.is_trial_active(user_id, course_id)

    @staticmethod
    def get_trial_expiry(user_id, course_id):
        """Get trial expiry datetime for a user in a course"""
        progress = LessonProgress.query.join(Lesson).join(Topic).filter(
            Topic.course_id == course_id,
            LessonProgress.user_id == user_id,
            LessonProgress.trial_started_at.isnot(None),
            LessonProgress.trial_cancelled == False
        ).first()
        
        if progress:
            return progress.trial_expires_at
        return None

    @staticmethod
    def update_course(course_id, **kwargs):
        """Update course information"""
        course = Course.query.get(course_id)
        
        if not course:
            return None, "Kursus tidak ditemukan"
        
        allowed_fields = ['title', 'description', 'grade_level', 'icon_class', 'color_theme']
        
        try:
            for key, value in kwargs.items():
                if key in allowed_fields and value:
                    setattr(course, key, value)
            
            db.session.commit()
            return course, "Kursus berhasil diupdate"
        except Exception as e:
            db.session.rollback()
            return None, f"Error: {str(e)}"

    @staticmethod
    def delete_course(course_id):
        """Delete a course"""
        course = Course.query.get(course_id)
        
        if not course:
            return False, "Kursus tidak ditemukan"
        
        try:
            db.session.delete(course)
            db.session.commit()
            return True, "Kursus berhasil dihapus"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    # Topic methods
    @staticmethod
    def create_topic(course_id, title, order=0):
        """Create a new topic in a course"""
        course = Course.query.get(course_id)
        
        if not course:
            return None, "Kursus tidak ditemukan"
        
        topic = Topic(title=title, course_id=course_id, order=order)
        
        try:
            db.session.add(topic)
            db.session.commit()
            return topic, "Topik berhasil dibuat"
        except Exception as e:
            db.session.rollback()
            return None, f"Error: {str(e)}"

    @staticmethod
    def get_topics_in_course(course_id):
        """Get all topics in a course"""
        return Topic.query.filter_by(course_id=course_id).order_by(Topic.order).all()

    # Lesson methods
    @staticmethod
    def create_lesson(topic_id, title, content_type='text', content_url=None, text_content=None, order=0):
        """Create a new lesson in a topic"""
        topic = Topic.query.get(topic_id)
        
        if not topic:
            return None, "Topik tidak ditemukan"
        
        lesson = Lesson(
            title=title,
            content_type=content_type,
            content_url=content_url,
            text_content=text_content,
            topic_id=topic_id,
            order=order
        )
        
        try:
            db.session.add(lesson)
            db.session.commit()
            return lesson, "Pembelajaran berhasil dibuat"
        except Exception as e:
            db.session.rollback()
            return None, f"Error: {str(e)}"

    @staticmethod
    def get_lessons_in_topic(topic_id):
        """Get all lessons in a topic"""
        return Lesson.query.filter_by(topic_id=topic_id).order_by(Lesson.order).all()

    @staticmethod
    def get_lesson_by_id(lesson_id):
        """Get lesson by ID"""
        return Lesson.query.get(lesson_id)
