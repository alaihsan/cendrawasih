"""
Seed script untuk populate database dengan sample data
Run: flask shell
>>> from app.seeds import seed_data
>>> seed_data()
"""

from app import db
from app.models.user import User
from app.models.course import Course, Topic
from app.models.lesson import Lesson


def seed_data():
    """Populate database with sample data"""
    
    # Clear existing data
    print("Clearing existing data...")
    Lesson.query.delete()
    Topic.query.delete()
    Course.query.delete()
    User.query.delete()
    db.session.commit()
    
    print("Creating sample users...")
    
    # Create teacher user
    teacher = User(username='pengajar1', email='pengajar@cendrawasih.id', role='teacher')
    teacher.set_password('password123')
    db.session.add(teacher)
    db.session.flush()
    
    # Create student account
    student = User(username='pelajar1', email='pelajar@cendrawasih.id', role='student')
    student.set_password('password123')
    db.session.add(student)
    db.session.commit()
    
    print("Creating sample courses...")
    
    # Course 1: Introduction to Python
    course1 = Course(
        title='Pengenalan Python untuk Pemula',
        description='Pelajari dasar-dasar pemrograman Python dari nol hingga bisa membuat program sederhana.',
        grade_level='Semua Level',
        instructor_id=teacher.id,
        icon_class='fa-code',
        color_theme='emerald'
    )
    db.session.add(course1)
    db.session.flush()
    
    # Course 2: Web Development
    course2 = Course(
        title='Web Development dengan Flask',
        description='Bangun aplikasi web modern menggunakan Flask dan teknologi web terkini.',
        grade_level='Intermediate',
        instructor_id=teacher.id,
        icon_class='fa-globe',
        color_theme='blue'
    )
    db.session.add(course2)
    db.session.flush()
    
    print("Creating topics and lessons...")
    
    # Topics for Course 1
    topic1_1 = Topic(title='Pengenalan Python', order=1, course_id=course1.id)
    topic1_2 = Topic(title='Variabel dan Tipe Data', order=2, course_id=course1.id)
    topic1_3 = Topic(title='Kontrol Alur Program', order=3, course_id=course1.id)
    
    db.session.add_all([topic1_1, topic1_2, topic1_3])
    db.session.flush()
    
    # Lessons untuk Topic 1
    lesson1_1_1 = Lesson(title='Apa itu Python?', content_type='text', topic_id=topic1_1.id, order=1,
                         text_content='Python adalah bahasa pemrograman yang mudah dipelajari dan sangat populer di industri teknologi.')
    lesson1_1_2 = Lesson(title='Setup Environment Python', content_type='text', topic_id=topic1_1.id, order=2,
                         text_content='Dalam pembelajaran ini, kita akan setup environment Python di komputer Anda.')
    lesson1_1_3 = Lesson(title='Program Hello World Pertama', content_type='text', topic_id=topic1_1.id, order=3,
                         text_content='Mari kita buat program pertama dengan print("Hello World")')
    
    db.session.add_all([lesson1_1_1, lesson1_1_2, lesson1_1_3])
    db.session.flush()
    
    # Lessons untuk Topic 2
    lesson1_2_1 = Lesson(title='Pengenalan Variabel', content_type='text', topic_id=topic1_2.id, order=1,
                         text_content='Variabel adalah tempat penyimpanan data di dalam program.')
    lesson1_2_2 = Lesson(title='Tipe Data Dasar', content_type='text', topic_id=topic1_2.id, order=2,
                         text_content='Python memiliki beberapa tipe data dasar seperti int, float, string, dan boolean.')
    
    db.session.add_all([lesson1_2_1, lesson1_2_2])
    db.session.flush()
    
    # Lessons untuk Topic 3
    lesson1_3_1 = Lesson(title='If-Else Statement', content_type='text', topic_id=topic1_3.id, order=1,
                         text_content='If-Else digunakan untuk membuat keputusan dalam program.')
    lesson1_3_2 = Lesson(title='Loop: For dan While', content_type='text', topic_id=topic1_3.id, order=2,
                         text_content='Loop digunakan untuk menjalankan kode berulang kali.')
    
    db.session.add_all([lesson1_3_1, lesson1_3_2])
    db.session.flush()
    
    # Topics for Course 2
    topic2_1 = Topic(title='Pengenalan Flask', order=1, course_id=course2.id)
    topic2_2 = Topic(title='Routing dan Views', order=2, course_id=course2.id)
    
    db.session.add_all([topic2_1, topic2_2])
    db.session.flush()
    
    # Lessons untuk Topic Flask
    lesson2_1_1 = Lesson(title='Flask Framework Basics', content_type='text', topic_id=topic2_1.id, order=1,
                         text_content='Flask adalah micro web framework untuk Python yang ringan dan fleksibel.')
    lesson2_1_2 = Lesson(title='Setup Project Flask', content_type='text', topic_id=topic2_1.id, order=2,
                         text_content='Pelajari cara setup project Flask dari awal.')
    
    db.session.add_all([lesson2_1_1, lesson2_1_2])
    db.session.flush()
    
    # Lessons untuk Routing
    lesson2_2_1 = Lesson(title='Membuat Route Pertama', content_type='text', topic_id=topic2_2.id, order=1,
                         text_content='Mari kita buat route pertama dengan Flask decorator @app.route()')
    lesson2_2_2 = Lesson(title='URL Parameters dan Query String', content_type='text', topic_id=topic2_2.id, order=2,
                         text_content='Belajar cara menangani parameter dalam URL dan query string.')
    
    db.session.add_all([lesson2_2_1, lesson2_2_2])
    db.session.flush()
    
    # Enroll student to courses
    student.enrolled_courses.append(course1)
    student.enrolled_courses.append(course2)
    
    db.session.commit()
    
    print("✅ Sample data created successfully!")
    print(f"   - Teacher: pengajar@cendrawasih.id (password: password123)")
    print(f"   - Student: pelajar@cendrawasih.id (password: password123)")
    print(f"   - Courses: {Course.query.count()}")
    print(f"   - Topics: {Topic.query.count()}")
    print(f"   - Lessons: {Lesson.query.count()}")


def clear_data():
    """Clear all data from database"""
    print("Clearing all data...")
    Lesson.query.delete()
    Topic.query.delete()
    Course.query.delete()
    User.query.delete()
    db.session.commit()
    print("✅ All data cleared!")
