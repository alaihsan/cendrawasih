from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, IntegerField, BooleanField
from wtforms.fields import FileField
from wtforms.validators import DataRequired, Length, Optional

class CourseForm(FlaskForm):
    title = StringField('Judul Kursus', validators=[
        DataRequired(message='Judul kursus diperlukan'),
        Length(min=5, max=200, message='Judul harus 5-200 karakter')
    ])
    description = TextAreaField('Deskripsi', validators=[
        DataRequired(message='Deskripsi diperlukan'),
        Length(min=10, max=1000, message='Deskripsi harus 10-1000 karakter')
    ])
    grade_level = StringField('Tingkat', validators=[
        Optional(),
        Length(max=100)
    ])
    icon_class = StringField('Icon FontAwesome', validators=[
        Optional(),
        Length(max=50)
    ], default='fa-book')
    color_theme = SelectField('Warna Tema', choices=[
        ('emerald', 'Emerald'),
        ('blue', 'Blue'),
        ('purple', 'Purple'),
        ('red', 'Red'),
        ('yellow', 'Yellow')
    ], default='emerald')
    submit = SubmitField('Simpan Kursus')

class TopicForm(FlaskForm):
    title = StringField('Judul Topik', validators=[
        DataRequired(message='Judul topik diperlukan'),
        Length(min=3, max=150, message='Judul harus 3-150 karakter')
    ])
    order = IntegerField('Urutan', validators=[Optional()], default=0)
    submit = SubmitField('Simpan Topik')

class LessonForm(FlaskForm):
    title = StringField('Judul Pembelajaran', validators=[
        DataRequired(message='Judul pembelajaran diperlukan'),
        Length(min=3, max=150)
    ])
    content_type = SelectField('Tipe Konten', choices=[
        ('text', 'Text'),
        ('video', 'Video Upload'),
        ('video_url', 'Video URL'),
        ('pdf', 'PDF'),
        ('quiz', 'Quiz')
    ], default='text')
    content_url = StringField('URL Konten', validators=[Optional(), Length(max=255)])
    
    # Video Upload Field
    video_file = FileField('Unggah Video', validators=[Optional()])
    
    # Image/Thumbnail Upload Field
    image_file = FileField('Unggah Gambar/Thumbnail', validators=[Optional()])
    
    text_content = TextAreaField('Konten Teks', validators=[Optional()])
    order = IntegerField('Urutan', validators=[Optional()], default=0)
    submit = SubmitField('Simpan Pembelajaran')

class QuizQuestionForm(FlaskForm):
    question_text = TextAreaField('Teks Pertanyaan', validators=[DataRequired()])
    
    # Opsi jawaban (Sederhanakan jadi 4 opsi untuk demo)
    option1 = StringField('Opsi 1', validators=[DataRequired()])
    is_correct1 = BooleanField('Benar')
    
    option2 = StringField('Opsi 2', validators=[DataRequired()])
    is_correct2 = BooleanField('Benar')
    
    option3 = StringField('Opsi 3', validators=[DataRequired()])
    is_correct3 = BooleanField('Benar')
    
    option4 = StringField('Opsi 4', validators=[DataRequired()])
    is_correct4 = BooleanField('Benar')
    
    submit = SubmitField('Simpan Pertanyaan')
