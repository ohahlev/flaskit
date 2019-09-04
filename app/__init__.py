from flask import Flask, request, session
from flask_moment import Moment
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_json import FlaskJSON
from app import util
from flask_babel import Babel

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


app = Flask(__name__)
app.wsgi_app = ReverseProxied(app.wsgi_app)

app.config.from_object("app.config")
db = SQLAlchemy(app)
mail = Mail(app)
app.config["DEBUG_TB_TEMPLATE_EDITOR_ENABLED"] = True
app.config["DEBUG_TB_PROFILER_ENABLED"] = True
toolbar = DebugToolbarExtension(app)
bcrypt = Bcrypt(app)
moment = Moment(app)
moment.init_app(app)

FlaskJSON(app)

from app.logger_setup import logger
from app.models import User
from app.views import error

from app.views.backend import (
    user as userbe
)
from app.views.frontend import (
    site as sitefe, user as userfe
)

app.register_blueprint(userbe.bp)

app.register_blueprint(sitefe.bp)
app.register_blueprint(userfe.bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "userfe.login"

app.add_url_rule("/uploads/<path:filename>", endpoint="uploads", view_func=app.send_static_file)


@login_manager.user_loader
def load_user(id):
    return User.query.filter(User.id == id).first()

app.config.from_pyfile('mysettings.cfg')
babel = Babel(app)

@babel.localeselector
def get_locale():
    try:
        lang = session["lang"]
    except KeyError:
        lang = request.app.config["LANG"]
        session.setdefault("lang", lang)
    return lang
