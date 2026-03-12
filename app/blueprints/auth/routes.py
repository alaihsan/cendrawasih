from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.blueprints.auth import bp
from app.forms.auth_forms import LoginForm, RegisterForm, ProfileForm, ChangePasswordForm
from app.services.user_service import UserService
from app import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user, message = UserService.authenticate_user(form.email.data, form.password.data)
        
        if user:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_has_allowed_host_and_scheme(next_page):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash(message, 'danger')
    
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user, message = UserService.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
            role=form.role.data
        )
        
        if user:
            flash(f'Selamat! Akun Anda berhasil dibuat. Silakan login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page with edit functionality"""
    user = UserService.get_user_by_id(current_user.id)
    profile_form = ProfileForm(current_user.username, current_user.email)
    password_form = ChangePasswordForm()
    
    # Check which form was submitted by looking for unique fields
    if request.method == 'POST':
        if 'username' in request.form and profile_form.validate_on_submit():
            current_user.username = profile_form.username.data
            current_user.email = profile_form.email.data
            db.session.commit()
            flash('Profil Anda berhasil diperbarui!', 'success')
            return redirect(url_for('auth.profile'))
            
        if 'old_password' in request.form and password_form.validate_on_submit():
            if current_user.check_password(password_form.old_password.data):
                current_user.set_password(password_form.new_password.data)
                db.session.commit()
                flash('Password Anda berhasil diubah!', 'success')
                return redirect(url_for('auth.profile'))
            else:
                flash('Password lama salah.', 'danger')
            
    if request.method == 'GET':
        profile_form.username.data = current_user.username
        profile_form.email.data = current_user.email
        
    return render_template('auth/profile.html', user=user, 
                         profile_form=profile_form, 
                         password_form=password_form)

def url_has_allowed_host_and_scheme(url, allowed_hosts=None):
    """Check if URL has allowed host and scheme (for redirect validation)"""
    from urllib.parse import urlparse
    
    if allowed_hosts is None:
        allowed_hosts = set()
    
    parsed = urlparse(url)
    
    # Allow relative URLs
    if not parsed.netloc and url.startswith('/'):
        return True
    
    return False
