from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    StringField, PasswordField
)
from wtforms.validators import (
    DataRequired, Length, Email, Optional,
    EqualTo
)
from app.models.user import User
from app.util import Unique


class FormForgot(FlaskForm):

    email = StringField(validators=[DataRequired(), Email()], description="email")


class FormReset(FlaskForm):

    password = PasswordField(validators=[
        DataRequired(), Length(min=6),
        EqualTo("confirm", message="Passwords must match.")
    ], description="lock")
    confirm = PasswordField(description="lock")


class FormLogin(FlaskForm):

    email = StringField(validators=[DataRequired(), Email()], description="email")
    password = PasswordField(validators=[DataRequired()],
                             description="lock")
    next = StringField()


class FormRegister(FlaskForm):

    name = StringField(validators=[DataRequired(), Length(min=5, max=32)], description="account_circle")
    phone = StringField(validators=[Optional()], description="phone")
    email = StringField(validators=[DataRequired(), Email(), Unique(User, User.email,
                                                                    "This email address is already taken")],
                        description="email")

    password = PasswordField(validators=[
        DataRequired(), Length(min=6),
        EqualTo("confirm", message="Passwords must match.")
    ], description="lock")
    confirm = PasswordField(description="lock")


class FormEditProfile(FlaskForm):

    name = StringField(validators=[DataRequired(), Length(min=5, max=32)], description="account_circle")
    phone = StringField(validators=[Optional()], description="phone")
    photo = FileField()


class FormChangePassword(FlaskForm):

    password = PasswordField(validators=[
        DataRequired(), Length(min=6)], description="lock")
    new_password = PasswordField(validators=[
        DataRequired(), Length(min=6),
        EqualTo("confirm_new_password", message="Passwords must match.")
    ], description="lock")
    confirm_new_password = PasswordField(description="lock")


class FormEditProfileForAdmin(FlaskForm):

    name = StringField(validators=[DataRequired(), Length(min=5, max=32)], description="account_circle")
    phone = StringField(validators=[Optional()], description="phone")
    email = StringField(description="email")
    photo = FileField()
    password = PasswordField(validators=[
        EqualTo("confirm", message="Passwords must match.")
    ], description="lock")
    confirm = PasswordField(description="lock")


class FormCreateUser(FlaskForm):

    name = StringField(validators=[DataRequired(), Length(min=5, max=32)], description="account_circle")
    phone = StringField(validators=[Optional()], description="phone")
    email = StringField(validators=[DataRequired(), Email(),
            Unique(User, User.email, "This email address is already taken")],
            description="email")
    photo = FileField()
    password = PasswordField(validators=[
        DataRequired(), Length(min=6),
        EqualTo("confirm", message="Passwords must match.")
    ], description="lock")
    confirm = PasswordField(description="lock")
