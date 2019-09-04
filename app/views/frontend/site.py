from flask import (
    Blueprint, render_template, session, request,
    redirect
)

bp = Blueprint("sitefe", __name__)


@bp.route("/")
def index():
    return render_template("frontend/site/index.html", title="Home")


@bp.route("/lang", methods=["POST"])
def switch_lang():
    lang = request.form.get("selected_lang")
    try:
        session_lang = session["lang"]
        if lang != session_lang:
            session["lang"] = lang
    except KeyError:
        session["lang"] = lang
    current_page = request.form.get("current_page")
    if not current_page:
        return redirect("sitefe.index")

    return redirect(current_page)
