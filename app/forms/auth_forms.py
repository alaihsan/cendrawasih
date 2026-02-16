from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email diperlukan'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password diperlukan')
    ])
    remember_me = BooleanField('Ingat saya')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message='Username diperlukan'),
        Length(min=3, max=64, message='Username harus 3-64 karakter'),
        Regexp('^[A-Za-z0-9_]+$', message='Username hanya boleh huruf, angka, dan underscore')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email diperlukan'),
        Email(message='Format email tidak valid')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password diperlukan'),
        Length(min=6, message='Password minimal 6 karakter')
    ])
    password_confirm = PasswordField('Konfirmasi Password', validators=[
        DataRequired(message='Konfirmasi password diperlukan'),
        EqualTo('password', message='Password tidak cocok')
    ])
    role = SelectField('Sebagai', choices=[
        ('student', 'Pelajar'),
        ('teacher', 'Pengajar')
    ], validators=[DataRequired()], default='student')
    submit = SubmitField('Daftar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username sudah digunakan. Pilih username lain.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email sudah terdaftar. Silakan login atau gunakan email lain.')
