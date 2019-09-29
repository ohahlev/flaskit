from flask import (
    Blueprint, render_template, redirect, url_for,
    flash, abort, request
)
from app import db, logger, util
from app.models.article import Article
from app.models.contact import Contact
from app.forms.article import (
    FormCreateEditContactUs, FormCreateEditAboutUs
)
from app.util import role_required, ADMIN

bp = Blueprint("sitebe", __name__, url_prefix="/backend/site")


@bp.route("/", methods=["GET"])
@role_required([ADMIN])
def index():
    
    articles = Article.list()
    return render_template("backend/site/index.html", title="Site Management", articles=articles)


@bp.route("/edit/<type>", methods=["GET", "POST"])
@role_required([ADMIN])
def edit_article(type):

    if type.upper() == util.ABOUT:
        about = Article.find_about()
        if not about:
            abort(404)

        form = FormCreateEditAboutUs()

        if request.method == "GET":
            form.text.data = about.text

        if form.validate_on_submit():
            if about.text == form.text.data:
                flash("data not changes")    
            else:
                about.text = form.text.data
                try:
                    db.session.commit()
                    flash("about us information is updated")
                except Exception as err:
                    logger.exception(err)
                    flash("about us information can not be updated", "negative")
                
            return redirect(url_for("sitebe.edit_article", type=type))

        return render_template("backend/site/about.html", title="Edit About", form=form)

    elif type.upper() == util.CONTACT:
        
        contact_us = Article.find_contact()
        if not contact_us:
            contact_us = Article()

        contact = Contact.first()
        if not contact:
            contact = Contact()

        form = FormCreateEditContactUs()

        if request.method == "GET":
            form.text.data = contact_us.text
            form.phone1.data = contact.phone1
            form.phone2.data = contact.phone2
            form.email.data = contact.email

        if form.validate_on_submit():

            changed = False

            if form.phone1.data.strip() != contact.phone1:
                changed = True
                contact.phone1 = form.phone1.data.strip()

            if form.phone2.data.strip() != contact.phone2:
                changed = True
                contact.phone2 = form.phone2.data.strip()

            if form.email.data.strip() != contact.email:
                changed = True
                contact.email = form.email.data.strip()

            if form.text.data.strip() != contact_us.text:
                changed = True
                contact_us.text = form.text.data.strip()

            if changed is True:
                try:
                    db.session.commit()
                    flash("contact us information is updated")
                except Exception as err:
                    logger.exception(err)
                    flash("contact us information can not be updated", "negative")
            else:
                flash("data not changes")

            return redirect(url_for("sitebe.edit_article", type=type))

        return render_template("backend/site/contact.html", title="Edit Contact", form=form)
    else:
        abort(404)



