from flask import render_template
from flask_login import current_user
from app.blueprints.main import bp

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/dashboard')
def dashboard():
    if not current_user.is_authenticated:
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html', user=current_user)
