from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from blog.models import User
from blog.customValidation.custom_validation import passwd_strength

class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), passwd_strength], id="password_field")
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], id="confirm_password_field")
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError("Username already exists. Please choose a different name!")
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError("Email already exists. Please choose a different name!")

class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):

    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()

            if user:
                raise ValidationError("Username already exists. Please choose a different name!")
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError("Email already exists. Please choose a different name!")


class RequestResetForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError("There is no valid account with that email!")
        

class ResetPasswordForm(FlaskForm):

    password = PasswordField('Password', validators=[DataRequired(), Length(min=8), passwd_strength], id="password_field")
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')], id="confirm_password_field")
    submit = SubmitField('Reset Password')
