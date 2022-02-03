from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Length(min=4, max=50)], render_kw={'placeholder': 'Email'})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)], render_kw={'placeholder': 'Password'})
