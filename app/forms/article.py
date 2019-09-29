from flask_wtf import FlaskForm
from wtforms import (
    StringField,TextAreaField
)
from wtforms.validators import (
    Required, Length, Email, Optional
)


class FormCreateEditAboutUs(FlaskForm):
    text = TextAreaField(validators=[Required(), Length(min=32)],
        description="local_library")


class FormCreateEditContactUs(FlaskForm):
    text = TextAreaField(validators=[Required(), Length(min=32)], description="local_library")
    phone1 = StringField(validators=[Required(), Length(max=32)], description="phone")
    phone2 = StringField(validators=[Optional(), Length(max=32)], description="phone")
    email = StringField(validators=[Email()], description="email")