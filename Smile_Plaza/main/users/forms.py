from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (StringField, PasswordField, SubmitField, BooleanField, 
                     IntegerField, SelectField, TextAreaField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from main.models import User

class RegistrationForm(FlaskForm):
    FName = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    MidName = StringField('Middle Name',
                           validators=[Length(min=2, max=20)])
    LName = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    gender_choices = [('', 'Select Gender'), ('man', 'Man'), ('woman', 'Woman'), ('transgender man', 'Transgender Man'), 
                      ('transgender woman', 'Transgender Woman'), ('non-binary', 'Non-binary'), ('genderqueer', 'Genderqueer'),
                      ('two-spirit', 'Two-spirit'), ('other', 'Other')]
    gender = SelectField('Gender', choices=gender_choices, validators=[DataRequired()])
    birthday = StringField('Birthday',
                           validators=[DataRequired()])
    age = IntegerField('Age',
                           validators=[DataRequired()])
    contact = StringField('Contact',
                           validators=[DataRequired(), Length(min=11, max=11)])
    address = StringField('Address',
                           validators=[DataRequired()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first() #SELECT * FROM User WHERE username = username.data
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first() #SELECT * FROM User WHERE email = email.data
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
        
    def validate_contact(self, contact):
        user = User.query.filter_by(contact=contact.data).first() #SELECT * FROM User WHERE contact = contact.data
        if user:
            raise ValidationError('That contact is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    contact = StringField('Contact Number')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first() #SELECT * FROM User WHERE username = username.data
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first() #SELECT * FROM User WHERE email = email.data
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_contact(self, contact):
        if contact.data != current_user.contact:
            user = User.query.filter_by(contact=contact.data).first() #SELECT * FROM User WHERE contact = contact.data
            if user:
                raise ValidationError('That contact number is taken. Please choose a different one.')

      
class ContactForm(FlaskForm):
    name = StringField( validators=[DataRequired()])
    email = StringField(validators=[DataRequired(), Email()])
    contact_number = StringField(validators=[DataRequired(), Length(min=11, max=11)])
    subject = StringField(validators=[DataRequired()])
    message = TextAreaField( validators=[DataRequired()])
    submit = SubmitField('Send')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        'New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')