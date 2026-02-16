from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.blueprints.auth import bp
from app.forms.auth_forms import LoginForm, RegisterForm
from app.services.user_service import UserService

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

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = UserService.get_user_by_id(current_user.id)
    return render_template('auth/profile.html', user=user)

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
