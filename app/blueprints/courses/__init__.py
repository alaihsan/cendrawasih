from flask import Blueprint

bp = Blueprint('courses', __name__)

from app.blueprints.courses import routes
