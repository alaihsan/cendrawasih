import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kunci-rahasia-cendrawasih-dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:passwd@localhost/db_cendrawasih'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Konfigurasi Upload (untuk materi/video nanti)
    UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
    MEDIA_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, 'media')
    COMPRESSED_FOLDER = os.path.join(UPLOAD_FOLDER, 'compressed')
    HLS_FOLDER = os.path.join(UPLOAD_FOLDER, 'hls')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # Limit 100MB for video

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}