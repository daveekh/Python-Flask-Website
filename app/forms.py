from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), Length(min=8, max=80), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is taken')

# XD
# # routes.py -> comment hashed_password, change user password to form.password.data
# # models.py -> add Unique=True to password

#    def validate_password(self, password):
#        user = User.query.filter_by(password=password.data).first()
#        if user:
#            raise ValidationError('This password is taken by user \'' + user.username + '\'')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit')


class UpdateEmailForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is taken. Please choose another.')


class UpdatePasswordForm(FlaskForm):
    currentPassword = PasswordField('Current password', validators=[DataRequired(), Length(min=8, max=80)])
    newPassword = PasswordField('New password', validators=[DataRequired(), Length(min=8, max=80)])
    confirmPassword = PasswordField('Confirm password', validators=[DataRequired(), Length(min=8, max=80), EqualTo('newPassword')])
    submit = SubmitField('Submit')


class UpdateAvatarForm(FlaskForm):
    avatar = FileField('Avatar', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    content = TextAreaField('Post', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')












