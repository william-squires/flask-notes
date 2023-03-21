
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length


class RegisterUserForm(FlaskForm):
    """Form for registering users."""
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=3, max=20)])

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=8)]
    )

    email = EmailField(
        "Email",
        validators=[InputRequired(), Length(max=50)]
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)]
    )


class LoginUserForm(FlaskForm):
    """Form for logging in users"""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=3, max=20)])

    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )

class LogoutForm(FlaskForm):
    """empty form for CSRF on logout"""