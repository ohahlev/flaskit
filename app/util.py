from functools import wraps
from flask_login import (
    current_user
)
from flask import (
    flash, redirect, url_for
)
from wtforms.validators import (
    ValidationError
)
from sqlalchemy import and_
from datetime import datetime
import random, string
import app


API_EMAIL = "api"
API_PASSWORD = "4p1"

# article
ABOUT = "ABOUT"
CONTACT = "CONTACT"

# role
API = "API"
ADMIN = "ADMIN"
USER = "USER"

# default date time format
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# max per page
PER_PAGE = 10

# default sorted by field
DEFAULT_SORT = "last_updated"

# empty value
EMPTY = "3MPT2"

# default salt
DEFAULT_SALT = "DEFAULT-SALT"

# minute expire
TOKEN_TIMEOUT = 5

def role_required(argument):
    def real_decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return app.login_manager.unauthorized()
            allowed = False
            for role in current_user.roles:
                for role_ in argument:
                    if role.name == role_:
                        allowed = True
                        break
                if allowed is True:
                    break
            if allowed is False:
                flash("access denied", "negative")
                return redirect(url_for("sitefe.index"))
            return function(*args, **kwargs)
        return wrapper
    return real_decorator


class Unique(object):
    def __init__(self, model, field, message):
        self.model = model
        self.field = field
        self.message = message
    def __call__(self, form, field):
        check = self.model.query.filter(self.field == field.data).first()
        if check:
            raise ValidationError(self.message)


class UniqueEdit(object):
    def __init__(self, model, id, field, message):
        self.model = model
        self.field = field
        self.id = id
        self.message = message
    def __call__(self, form, field):
        check = self.model.query.filter(and_(self.field == field.data, self.id != form.id.data)).first()
        if check:
            raise ValidationError(self.message)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def convert_to_dict(obj):
    #  Populate the dictionary with object meta data
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }
    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)
    return obj_dict

def get_salt(starting_key):
    key = starting_key if starting_key is not None else DEFAULT_SALT
    return "{0} - {1}".format(key, datetime.now())

def generate_random(n):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))

