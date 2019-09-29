from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session
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

@bp.route("/lang", methods=["POST"])
def switch_lang():
    print("switch lange")
    lang = request.form.get("selected_lang")
    try:
        session_lang = session["lang"]
        if lang != session_lang:
            session["lang"] = lang
    except KeyError:
        session["lang"] = lang
    current_page = request.form.get("current_page")
    if not current_page:
        return redirect(url_for("sitefe.index"))
    return redirect(current_page)
