from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, IntegerField
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
        ('video', 'Video'),
        ('pdf', 'PDF')
    ], default='text')
    content_url = StringField('URL Konten', validators=[Optional(), Length(max=255)])
    text_content = TextAreaField('Konten Teks', validators=[Optional()])
    order = IntegerField('Urutan', validators=[Optional()], default=0)
    submit = SubmitField('Simpan Pembelajaran')
