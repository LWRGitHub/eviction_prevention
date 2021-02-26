from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField, TextAreaField, IntegerField, FloatField, PasswordField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, URL
from eviction_prevention_app.models import Job, Event, TitleCategory, User

class EventForm(FlaskForm):
    """Form for adding/updating a Event."""
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=80)])
    Description = StringField('Name', validators=[DataRequired(), Length(min=1, max=200)])
    address = TextAreaField('Address', validators=[DataRequired(), Length(min=3, max=300)])
    
    submit = SubmitField('Submit')

class JobForm(FlaskForm):
    """Form for adding/updating a Job."""

    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=80)])
    Description = StringField('Name', validators=[DataRequired(), Length(min=1, max=200)])
    pay = FloatField('Price', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired(), Length(min=1, max=80)])
    photo_url = StringField('Photo url', validators=[DataRequired(), URL()])
    
    submit = SubmitField('Submit')

class SignUpForm(FlaskForm):
    """ Form for new user sign up """
    username = StringField('User Name',
        validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    """ Form for logging in """
    username = StringField('User Name',
        validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')
