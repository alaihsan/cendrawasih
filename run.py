#!/usr/bin/env python
import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.course import Course, Topic
from app.models.lesson import Lesson

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 
        'User': User, 
        'Course': Course, 
        'Topic': Topic, 
        'Lesson': Lesson
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
