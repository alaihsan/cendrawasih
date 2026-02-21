from flask import render_template, request
from flask_login import current_user, login_required
from app.blueprints.main import bp
from app.services.course_service import CourseService
from app.services.progress import ProgressService
from app.models.course import Course

@bp.route('/')
def index():
    # Get featured courses (first 3 courses)
    featured_courses = CourseService.get_all_courses()[:3]
    return render_template('index.html', featured_courses=featured_courses)

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get pagination parameter
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get enrolled courses with pagination - order by creation date descending
    enrolled_courses_query = current_user.enrolled_courses.order_by(Course.created_at.desc())
    total_courses = enrolled_courses_query.count()
    
    # Calculate pagination
    total_pages = (total_courses + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    enrolled_courses = enrolled_courses_query.offset(offset).limit(per_page).all()
    
    # Get progress data for each course
    courses_with_progress = []
    for course in enrolled_courses:
        progress_data, _ = ProgressService.get_user_progress(current_user.id, course.id)
        courses_with_progress.append({
            'course': course,
            'progress': progress_data
        })
    
    # Calculate quick stats
    total_enrolled = total_courses
    total_lessons_completed = 0
    total_lessons = 0
    
    for item in courses_with_progress:
        progress = item['progress']
        if progress:
            total_lessons_completed += progress.get('completed_lessons', 0)
            total_lessons += progress.get('total_lessons', 0)
    
    avg_progress = 0
    if total_lessons > 0:
        avg_progress = round((total_lessons_completed / total_lessons) * 100)
    
    return render_template(
        'dashboard.html', 
        user=current_user,
        courses_with_progress=courses_with_progress,
        total_enrolled=total_enrolled,
        total_lessons_completed=total_lessons_completed,
        total_lessons=total_lessons,
        avg_progress=avg_progress,
        current_page=page,
        total_pages=total_pages,
        has_prev=(page > 1),
        has_next=(page < total_pages)
    )
