from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import Form, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, ValidationError


#Registration Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords do not match')])
    submit = SubmitField('Create an account')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Your Email Adress', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log In')

#Password Reset Request Form
class RequestResetForm(FlaskForm):
    email = StringField('Your Email Adress', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Password Request')

# -------- Update User Details -------------
class UpdateUserForm(FlaskForm):
    username = StringField('Enter a New Username :', [validators.optional(), validators.Length(min=2, max=20)])
    email = StringField('Enter a New Email Address :', [validators.optional(), validators.DataRequired(), validators.Email()])
    current_password = PasswordField('Enter Current Password', [validators.optional(), validators.DataRequired()])
    new_password = PasswordField('Create New Password', [validators.optional(), validators.DataRequired(), validators.Length(min=6, max=60)])
    new_password_confirm = PasswordField('Confirm New Password', validators=[EqualTo('new_password', message='Passwords do not match')])
    picture = FileField('Update Your Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update your profile')

# -------- Search Form ---------------
class SearchForm(FlaskForm):
    search=StringField('Start a New Search', description="Search Books", validators=[DataRequired(), Length(min=2)])

# -------- Submit Review Form ---------------
class SubmitReviewForm(FlaskForm):
    rating = SelectField('Score :', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')])
    review = TextAreaField('Write a review', validators=[DataRequired()])
    submit = SubmitField('Post Now')
