from flask import (
    Blueprint, render_template
)

bp = Blueprint("sitefe", __name__)


@bp.route("/")
def index():
    return render_template("frontend/site/index.html", title="Home")