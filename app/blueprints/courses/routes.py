from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.blueprints.courses import bp
from app.services.course_service import CourseService
from app.services.progress import ProgressService

@bp.route('/list')
def list():
    """List all courses"""
    courses = CourseService.get_all_courses()
    user_enrolled = {}
    
    if current_user.is_authenticated:
        for course in courses:
            user_enrolled[course.id] = CourseService.is_student_enrolled(current_user.id, course.id)
    
    return render_template('courses/list.html', courses=courses, user_enrolled=user_enrolled)

@bp.route('/<int:course_id>')
def detail(course_id):
    """View course detail"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('courses.list'))
    
    topics = CourseService.get_topics_in_course(course_id)
    is_enrolled = False
    progress_data = None
    
    if current_user.is_authenticated:
        is_enrolled = CourseService.is_student_enrolled(current_user.id, course_id)
        if is_enrolled:
            progress_data, _ = ProgressService.get_user_progress(current_user.id, course_id)
    
    return render_template('courses/detail.html', course=course, topics=topics, 
                         is_enrolled=is_enrolled, progress_data=progress_data)

@bp.route('/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll(course_id):
    """Enroll user to a course"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('courses.list'))
    
    success, message = CourseService.enroll_student(current_user.id, course_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('courses.detail', course_id=course_id))

@bp.route('/<int:course_id>/unenroll', methods=['POST'])
@login_required
def unenroll(course_id):
    """Unenroll user from a course"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('courses.list'))
    
    success, message = CourseService.unenroll_student(current_user.id, course_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('courses.detail', course_id=course_id))

@bp.route('/<int:course_id>/my-progress')
@login_required
def my_progress(course_id):
    """View user progress in a course"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('courses.list'))
    
    is_enrolled = CourseService.is_student_enrolled(current_user.id, course_id)
    
    if not is_enrolled:
        flash('Anda belum mendaftar kursus ini', 'danger')
        return redirect(url_for('courses.detail', course_id=course_id))
    
    progress_data, _ = ProgressService.get_user_progress(current_user.id, course_id)
    
    return render_template('courses/progress.html', course=course, progress_data=progress_data)

@bp.route('/lesson/<int:lesson_id>')
@login_required
def view_lesson(lesson_id):
    """View a lesson"""
    lesson = CourseService.get_lesson_by_id(lesson_id)
    
    if not lesson:
        flash('Pembelajaran tidak ditemukan', 'danger')
        return redirect(url_for('main.dashboard'))
    
    topic = lesson.topic
    course = topic.course
    
    # Check if user is enrolled in this course
    is_enrolled = CourseService.is_student_enrolled(current_user.id, course.id)
    
    if not is_enrolled:
        flash('Anda belum mendaftar kursus ini', 'danger')
        return redirect(url_for('courses.detail', course_id=course.id))
    
    # Get lesson progress
    progress, _ = ProgressService.get_lesson_progress(current_user.id, lesson_id)
    
    # Get next and previous lessons
    lessons_in_topic = CourseService.get_lessons_in_topic(topic.id)
    current_index = next((i for i, l in enumerate(lessons_in_topic) if l.id == lesson_id), None)
    
    prev_lesson = lessons_in_topic[current_index - 1] if current_index and current_index > 0 else None
    next_lesson = lessons_in_topic[current_index + 1] if current_index is not None and current_index < len(lessons_in_topic) - 1 else None
    
    # Prepare video sources for quality selector
    video_sources = []
    if lesson.content_type == 'video' and lesson.compressed_video_versions:
        # Build sources array from compressed versions
        versions_map = lesson.compressed_video_versions
        
        # Order: low, medium, high, webm (with quality labels)
        quality_order = [
            ('low', 'Low (480p)', 'video/mp4'),
            ('medium', 'Medium (720p)', 'video/mp4'),
            ('high', 'High (1080p)', 'video/mp4'),
            ('webm', 'WebM (720p)', 'video/webm')
        ]
        
        for key, label, mime_type in quality_order:
            if key in versions_map and versions_map[key]:
                video_sources.append({
                    'src': versions_map[key],
                    'type': mime_type,
                    'quality': label.split('(')[0].strip(),  # Extract just the quality level
                    'label': label
                })
    
    return render_template('courses/lesson.html', lesson=lesson, topic=topic, course=course,
                         progress=progress, prev_lesson=prev_lesson, next_lesson=next_lesson,
                         video_sources=video_sources)

@bp.route('/<int:course_id>/preview')
def course_preview(course_id):
    """Preview course - show overview and first lesson"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('courses.list'))
    
    # Get first topic and lesson for preview
    first_topic = course.topics.order_by('order').first() if course.topics else None
    first_lesson = first_topic.lessons.order_by('order').first() if first_topic else None
    
    # Build video sources for first lesson if it's a video
    video_sources = []
    if first_lesson and first_lesson.content_type == 'video' and first_lesson.compressed_video_versions:
        versions_map = first_lesson.compressed_video_versions
        quality_order = [
            ('low', 'Low (480p)', 'video/mp4'),
            ('medium', 'Medium (720p)', 'video/mp4'),
            ('high', 'High (1080p)', 'video/mp4'),
            ('webm', 'WebM (720p)', 'video/webm')
        ]
        
        for key, label, mime_type in quality_order:
            if key in versions_map and versions_map[key]:
                video_sources.append({
                    'src': versions_map[key],
                    'type': mime_type,
                    'quality': label.split('(')[0].strip(),
                    'label': label
                })
    
    # Calculate course stats
    total_lessons = sum(len(topic.lessons) for topic in course.topics)
    total_topics = len(course.topics)
    is_enrolled = current_user.is_authenticated and CourseService.is_student_enrolled(current_user.id, course_id)
    
    return render_template('courses/preview.html', 
                         course=course,
                         first_lesson=first_lesson,
                         first_topic=first_topic,
                         video_sources=video_sources,
                         total_lessons=total_lessons,
                         total_topics=total_topics,
                         is_enrolled=is_enrolled)

@bp.route('/lesson/<int:lesson_id>/mark-complete', methods=['POST'])
@login_required
def mark_complete(lesson_id):
    """Mark a lesson as complete"""
    success, message = ProgressService.mark_lesson_complete(current_user.id, lesson_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(request.referrer or url_for('main.dashboard'))
