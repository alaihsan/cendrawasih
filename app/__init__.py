from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from app.config import config

# Inisialisasi Ekstensi di luar create_app agar bisa diimport file lain
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login' # Mengarahkan user yang belum login ke halaman login

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Memuat konfigurasi dari config.py
    app.config.from_object(config[config_name])

    # Menghubungkan ekstensi ke aplikasi yang baru dibuat
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Setup user_loader untuk login manager
    from app.models.user import User
    
    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrasi Blueprints (Modularisasi Route)
    from app.blueprints.main import bp as main_bp
    from app.blueprints.auth import bp as auth_bp
    from app.blueprints.courses import bp as courses_bp
    from app.blueprints.api import bp as api_bp
    from app.blueprints.admin import bp as admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

# Import models di bagian bawah untuk menghindari circular import
# Karena models sudah dipecah jadi folder, ini akan mengimpor app/models/__init__.py
from app import models