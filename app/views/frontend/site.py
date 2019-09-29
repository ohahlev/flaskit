from flask import (
    Blueprint, render_template, jsonify, send_file, redirect, url_for
)

bp = Blueprint("sitefe", __name__)

@bp.route("/")
def index():
    return render_template("frontend/site/index.html", title="Home")

@bp.route("/about")
def about():
    return render_template("frontend/site/about.html", title="About")


@bp.route("/contact")
def contact():
    return render_template("frontend/site/contact.html", title="Contact")

