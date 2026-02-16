from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.blueprints.admin import bp
from app.utils.decorators import teacher_required, admin_required
from app.forms.admin_forms import CourseForm, TopicForm, LessonForm
from app.services.course_service import CourseService
from app import db

# ============ DASHBOARD ============

@bp.route('/dashboard')
@login_required
def dashboard():
    """Admin/Teacher dashboard"""
    if current_user.role == 'admin':
        # Admin sees all statistics
        from app.models.user import User
        from app.models.course import Course
        total_users = User.query.count()
        total_courses = Course.query.count()
        total_students = User.query.filter_by(role='student').count()
        
        return render_template('admin/dashboard.html',
                             total_users=total_users,
                             total_courses=total_courses,
                             total_students=total_students)
    else:
        # Teacher sees only their courses
        courses = CourseService.get_courses_by_instructor(current_user.id)
        return render_template('admin/teacher-dashboard.html', courses=courses)

# ============ COURSES MANAGEMENT ============

@bp.route('/courses')
@login_required
def courses_list():
    """List courses (admin sees all, teacher sees own)"""
    if current_user.role == 'admin':
        courses = CourseService.get_all_courses()
    else:
        courses = CourseService.get_courses_by_instructor(current_user.id)
    
    return render_template('admin/courses/list.html', courses=courses)

@bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
def course_create():
    """Create new course"""
    if current_user.role not in ['teacher', 'admin']:
        flash('Hanya pengajar yang dapat membuat kursus', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course, message = CourseService.create_course(
            title=form.title.data,
            description=form.description.data,
            grade_level=form.grade_level.data,
            instructor_id=current_user.id,
            icon_class=form.icon_class.data,
            color_theme=form.color_theme.data
        )
        
        if course:
            flash('Kursus berhasil dibuat!', 'success')
            return redirect(url_for('admin.course_detail', course_id=course.id))
        else:
            flash(message, 'danger')
    
    return render_template('admin/courses/create.html', form=form)

@bp.route('/courses/<int:course_id>')
@login_required
def course_detail(course_id):
    """View course detail"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    # Check access
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Anda tidak memiliki akses ke kursus ini', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    topics = CourseService.get_topics_in_course(course_id)
    return render_template('admin/courses/detail.html', course=course, topics=topics)

@bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
def course_edit(course_id):
    """Edit course"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    # Check access
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Anda tidak memiliki akses ke kursus ini', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course, message = CourseService.update_course(
            course_id,
            title=form.title.data,
            description=form.description.data,
            grade_level=form.grade_level.data,
            icon_class=form.icon_class.data,
            color_theme=form.color_theme.data
        )
        
        if course:
            flash('Kursus berhasil diupdate!', 'success')
            return redirect(url_for('admin.course_detail', course_id=course.id))
        else:
            flash(message, 'danger')
    elif request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
        form.grade_level.data = course.grade_level
        form.icon_class.data = course.icon_class
        form.color_theme.data = course.color_theme
    
    return render_template('admin/courses/edit.html', form=form, course=course)

@bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
def course_delete(course_id):
    """Delete course"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course:
        flash('Kursus tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Anda tidak memiliki akses untuk menghapus kursus ini', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    success, message = CourseService.delete_course(course_id)
    
    if success:
        flash('Kursus berhasil dihapus!', 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.courses_list'))

# ============ TOPICS MANAGEMENT ============

@bp.route('/courses/<int:course_id>/topics/create', methods=['GET', 'POST'])
@login_required
def topic_create(course_id):
    """Create topic"""
    course = CourseService.get_course_by_id(course_id)
    
    if not course or (current_user.role != 'admin' and course.instructor_id != current_user.id):
        flash('Akses ditolak', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    form = TopicForm()
    if form.validate_on_submit():
        topic, message = CourseService.create_topic(
            course_id,
            title=form.title.data,
            order=form.order.data
        )
        
        if topic:
            flash('Topik berhasil dibuat!', 'success')
            return redirect(url_for('admin.course_detail', course_id=course_id))
        else:
            flash(message, 'danger')
    
    return render_template('admin/topics/create.html', form=form, course=course)

@bp.route('/topics/<int:topic_id>/edit', methods=['GET', 'POST'])
@login_required
def topic_edit(topic_id):
    """Edit topic"""
    from app.models.course import Topic
    topic = Topic.query.get(topic_id)
    
    if not topic:
        flash('Topik tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    course = topic.course
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Akses ditolak', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    form = TopicForm()
    if form.validate_on_submit():
        topic.title = form.title.data
        topic.order = form.order.data
        db.session.commit()
        
        flash('Topik berhasil diupdate!', 'success')
        return redirect(url_for('admin.course_detail', course_id=course.id))
    elif request.method == 'GET':
        form.title.data = topic.title
        form.order.data = topic.order
    
    return render_template('admin/topics/edit.html', form=form, topic=topic, course=course)

@bp.route('/topics/<int:topic_id>/delete', methods=['POST'])
@login_required
def topic_delete(topic_id):
    """Delete topic"""
    from app.models.course import Topic
    topic = Topic.query.get(topic_id)
    
    if not topic:
        flash('Topik tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    course = topic.course
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Akses ditolak', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    try:
        db.session.delete(topic)
        db.session.commit()
        flash('Topik berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin.course_detail', course_id=course.id))

# ============ LESSONS MANAGEMENT ============

@bp.route('/topics/<int:topic_id>/lessons/create', methods=['GET', 'POST'])
@login_required
def lesson_create(topic_id):
    """Create lesson"""
    from app.models.course import Topic
    topic = Topic.query.get(topic_id)
    
    if not topic:
        flash('Topik tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    course = topic.course
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Akses ditolak', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    form = LessonForm()
    if form.validate_on_submit():
        lesson, message = CourseService.create_lesson(
            topic_id,
            title=form.title.data,
            content_type=form.content_type.data,
            content_url=form.content_url.data,
            text_content=form.text_content.data,
            order=form.order.data
        )
        
        if lesson:
            flash('Pembelajaran berhasil dibuat!', 'success')
            return redirect(url_for('admin.course_detail', course_id=course.id))
        else:
            flash(message, 'danger')
    
    return render_template('admin/lessons/create.html', form=form, topic=topic, course=course)

@bp.route('/lessons/<int:lesson_id>/edit', methods=['GET', 'POST'])
@login_required
def lesson_edit(lesson_id):
    """Edit lesson"""
    lesson = CourseService.get_lesson_by_id(lesson_id)
    
    if not lesson:
        flash('Pembelajaran tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    topic = lesson.topic
    course = topic.course
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Akses ditolak', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    form = LessonForm()
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.content_type = form.content_type.data
        lesson.content_url = form.content_url.data
        lesson.text_content = form.text_content.data
        lesson.order = form.order.data
        db.session.commit()
        
        flash('Pembelajaran berhasil diupdate!', 'success')
        return redirect(url_for('admin.course_detail', course_id=course.id))
    elif request.method == 'GET':
        form.title.data = lesson.title
        form.content_type.data = lesson.content_type
        form.content_url.data = lesson.content_url
        form.text_content.data = lesson.text_content
        form.order.data = lesson.order
    
    return render_template('admin/lessons/edit.html', form=form, lesson=lesson, topic=topic, course=course)

@bp.route('/lessons/<int:lesson_id>/delete', methods=['POST'])
@login_required
def lesson_delete(lesson_id):
    """Delete lesson"""
    lesson = CourseService.get_lesson_by_id(lesson_id)
    
    if not lesson:
        flash('Pembelajaran tidak ditemukan', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    topic = lesson.topic
    course = topic.course
    if current_user.role != 'admin' and course.instructor_id != current_user.id:
        flash('Akses ditolak', 'danger')
        return redirect(url_for('admin.courses_list'))
    
    try:
        db.session.delete(lesson)
        db.session.commit()
        flash('Pembelajaran berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin.course_detail', course_id=course.id))

# ============ USER MANAGEMENT (ADMIN ONLY) ============

@bp.route('/users')
@admin_required
def users_list():
    """List all users (admin only)"""
    from app.models.user import User
    users = User.query.all()
    return render_template('admin/users/list.html', users=users)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def user_delete(user_id):
    """Delete user (admin only)"""
    from app.models.user import User
    from app.services.user_service import UserService
    
    user = User.query.get(user_id)
    
    if not user:
        flash('User tidak ditemukan', 'danger')
        return redirect(url_for('admin.users_list'))
    
    if user.id == current_user.id:
        flash('Anda tidak dapat menghapus akun Anda sendiri', 'danger')
        return redirect(url_for('admin.users_list'))
    
    success, message = UserService.delete_user(user_id)
    
    if success:
        flash('User berhasil dihapus!', 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('admin.users_list'))
