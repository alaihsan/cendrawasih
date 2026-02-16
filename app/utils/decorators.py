from functools import wraps
from flask import redirect, url_for, flash, current_app
from flask_login import current_user

def role_required(role):
    """Decorator untuk check user role access"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Silakan login terlebih dahulu', 'danger')
                return redirect(url_for('auth.login'))
            
            if current_user.role != role and current_user.role != 'admin':
                flash('Anda tidak memiliki akses ke halaman ini', 'danger')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def teacher_required(f):
    """Decorator untuk teacher/instructor access"""
    return role_required('teacher')(f)

def admin_required(f):
    """Decorator untuk admin access only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Silakan login terlebih dahulu', 'danger')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('Hanya admin yang dapat mengakses halaman ini', 'danger')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function
