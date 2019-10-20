from flask import (
    Blueprint, render_template, redirect,
    url_for, abort, flash, request, make_response
)
from flask_login import (
    login_user, logout_user, login_required,
    current_user
)
from itsdangerous import URLSafeTimedSerializer
from app import app, db, util, logger
from app.models.user import User
from app.models.role import Role
from app.forms.user import (
   FormRegister, FormReset, FormLogin, FormEditProfile,
   FormChangePassword, FormForgot
)
from datetime import datetime, timedelta
from app.toolbox import email

# Serializer for generating random tokens
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Create a user blueprint
bp = Blueprint("userfe", __name__, url_prefix="/user")


def expire_confirm_email_token(token):
    user = User.query.filter_by(token=token).first()
    if user:
        try:
            db.session.delete(user)
            print("deleted user: {}".format(user.name))
        except Exception as err:
            logger.exception(err)


def expire_reset_password_token(token):
    user = User.query.filter_by(token=token).first()
    if user:
        try:
            user.token = None
            db.session.commit()
            print("expire token = {}".format(token))
        except Exception as err:
            logger.exception(err)

@bp.route("/register", methods=["GET", "POST"])
def register():

    # can not register if already logged in
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("sitefe.index"))

    form = FormRegister()

    if form.validate_on_submit():

        user = User(
            name=form.name.data.strip(),
            phone=form.phone.data.strip(),
            email=form.email.data.strip(),
            password=form.password.data.strip()
        )

        # assign role as normal user
        user_role = Role.query.filter_by(name=util.USER).first()
        if user_role:
            user.roles.append(user_role)

        # insert the user in the database
        try:
            db.session.add(user)
            db.session.commit()

            subject = "Please confirm your email address."
            salt = util.get_salt(app.config["SALT_CONFIRM_EMAIL"])
            token = ts.dumps(user.email, salt=salt)

            user.token = token
            db.session.commit()

            confirm_url = url_for("userfe.confirm", token=token, _external=True)

            html = render_template("frontend/email/confirm.html",
                                   confirm_url=confirm_url)
            email.send(user.email, subject, html)

            now = datetime.now()
            now_plus_timeout = now + timedelta(minutes=util.TOKEN_TIMEOUT)

            app.apscheduler.add_job(func=expire_confirm_email_token, trigger='date', next_run_time=str(now_plus_timeout),
                                    args=[token], id=util.generate_random(5))

            flash("Check your email to confirm. You've got {} minutes before the link expires"
                  .format(util.TOKEN_TIMEOUT), "positive")

            return redirect(url_for("userfe.login"))

        except Exception as err:
            logger.exception(err)
            flash("can not register at this moment", "negative")
            return redirect(url_for("userfe.register"))
        finally:
            print("now in finally")
            user = User.query.filter_by(email=form.email.data.strip()).first()
            if user:
                print("found ghost user")
                db.session.delete(user)
                db.session.commit()

    return render_template("frontend/user/register.html", form=form, title="Register")

@bp.route("/confirm/<token>", methods=["GET"])
def confirm(token):

    try:
        user = User.query.filter_by(token=token).first()
    except Exception as err:
        logger.exception(err)
        flash("can not get user by token = {} from database".format(token), "negative")
        return redirect(url_for("sitefe.index"))

    if not user:
        abort(404)

    try:
        user.confirmed = True
        user.token = None
        db.session.commit()
    except Exception as err:
        logger.exception(err)
        flash("can not confirm email at this moment", "negative")
        return redirect(url_for("userfe.confirm", token=token))

    flash("Your email address has been confirmed, you can log in.", "positive")
    return redirect(url_for("userfe.login"))

@bp.route("/login", defaults={"next1": None}, methods=["GET", "POST"])
@bp.route("/login?next=<next1>", methods=["GET", "POST"])
def login(next1):

    invalid_user = "invalid user"

    form = FormLogin()

    next_page = ""
    if request.method == "GET":
        next_page = request.args.get("next")
        form.next.data = next_page
    elif request.method == "POST":
        next_page = form.next.data

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # check if user exists
        if user is None:
            flash(invalid_user, "negative")
            return redirect(url_for("userfe.login"))

        # check if already confirm
        if user.confirmed is False:
            flash("email = {} didn't confirm yet".format(form.email.data), "negative")
            return redirect(url_for("userfe.login"))

        # check if user is deleted
        if user.deleted is True:
            flash("email = {} is deleted from system".format(form.email.data), "negative")
            return redirect(url_for("userfe.login"))

        # check the password is correct
        if user.check_password(form.password.data) is False:
            flash(invalid_user, "negative")
            return redirect(url_for("userfe.login"))

        # everything is good to go

        #agent = request.headers.get("User-Agent")
        #print("user agent = {0}".format(agent))
        #print("mobile user? == {0}".format(util.is_mobile_user(agent)))

        login_user(user)
        flash("Succesfully logged in.", "positive")

        if next_page:
            resp = make_response(redirect(next_page))
        else:
            resp = make_response(redirect(url_for("sitefe.index")))

        #resp.set_cookie("user", value=user.email)
        return resp

    if next_page is None:
        return render_template("frontend/user/login.html", form=form, title="Log in")

    return render_template("frontend/user/login.html", form=form, title="Log in", next=next_page)



@bp.route("/logout")
def logout():

    # can not logout if not yet logged in
    if request.method == "GET" and current_user.is_authenticated == False:
        return redirect(url_for("sitefe.index"))
    logout_user()

    resp = make_response(redirect(url_for("sitefe.index")))
    #resp.set_cookie("user", "", expires=0)
    flash("Succesfully logout out.", "positive")
    return resp


@bp.route("/profile/<int:id>", methods=["GET", "POST"])
@login_required
def profile(id):

    form_edit_profile = FormEditProfile()
    form_change_password = FormChangePassword()
    user = User.query.filter_by(email=current_user.email).first()

    if request.method == "GET":
        form_edit_profile.name.data = user.name
        form_edit_profile.phone.data = user.phone

    if id == 1:
        if form_edit_profile.validate_on_submit():
            if user.name == form_edit_profile.name.data.strip() and user.phone == form_edit_profile.phone.data.strip():
                flash("same name and same phone")
                return redirect(url_for("userfe.profile"))

            changed = False
            if user.name != form_edit_profile.name.data.strip():
                changed = True
                user.name = form_edit_profile.name.data.strip()
            if user.phone != form_edit_profile.phone.data.strip():
                changed = True
                user.phone = form_edit_profile.phone.data.strip()
            if changed is True:
                db.session.commit()
                flash("profile is updated")
                return redirect(url_for("userfe.profile", id=1))

        return render_template("frontend/user/profile.html", title="Edit Profile",  id=1,
                               form_edit_profile=form_edit_profile, form_change_password=form_change_password,
                               user=user)
    elif id == 2:
        if form_change_password.validate_on_submit():
            if user.check_password(form_change_password.password.data.strip()) is False:
                flash("current password is wrong")
                return redirect(url_for("userfe.profile", title="Edit Profile", id=2,
                                        form_edit_profile=form_edit_profile, form_change_password=form_change_password,
                                        user=user))
            else:
                user.password = form_change_password.new_password.data.strip()
                try:
                    db.session.commit()
                except Exception as err:
                    logger.exception(err)
                    flash("can not change password at this moment", "negative")
                    return redirect(url_for("userfe.profile", id=2))

                flash("password is changed")
                return redirect(url_for("userfe.profile", title="Edit Profile", id=2,
                                        form_edit_profile=form_edit_profile, form_change_password=form_change_password,
                                        user=user))
    return render_template("frontend/user/profile.html", title="Edit Profile",
                           form_edit_profile=form_edit_profile, form_change_password=form_change_password, user=user)


@bp.route("/forgot", methods=["GET", "POST"])
def forgot():

    # can not forgot password if already logged in
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("sitefe.index"))

    form = FormForgot()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            subject = "Reset your password."

            salt = util.get_salt(app.config["SALT_RESET_PASSWORD"])
            token = ts.dumps(user.email, salt=salt)

            try:
                user.token = token
                db.session.commit()
            except Exception as err:
                logger.exception(err)
                flash("can not reset password at this moment", "negative")
                return redirect(url_for("userfe.forgot"))

            resetUrl = url_for("userfe.reset", token=token, _external=True)
            html = render_template("frontend/email/reset.html", reset_url=resetUrl)
            email.send(user.email, subject, html)

            now = datetime.now()
            now_plus_timeout = now + timedelta(minutes=util.TOKEN_TIMEOUT)

            app.apscheduler.add_job(func=expire_reset_password_token, trigger='date', next_run_time=str(now_plus_timeout),
                                    args=[token], id=util.generate_random(5))

            flash("Check your emails to reset your password. You've got {} minutes before the link expires"
                  .format(util.TOKEN_TIMEOUT), "positive")
            return redirect(url_for("sitefe.index"))
        else:
            flash("Unknown email address.", "negative")
            return redirect(url_for("userfe.forgot"))
    return render_template("frontend/user/forgot.html", form=form)


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):

    try:
        user = User.query.filter_by(token=token).first()
    except Exception as err:
        logger.exception(err)
        flash("can not get user by token = {} from database".format(token), "negative")
        return redirect(url_for("userfe.reset", token=token))

    if not user:
        abort(404)

    form = FormReset()
    if form.validate_on_submit():

        if user:
            try:
                user.password = form.password.data.strip()
                user.token = None
                db.session.commit()
            except Exception as err:
                logger.exception(err)
                flash("can not reset password at this moment", "negative")
                return redirect(url_for("userfe.reset", token=token))

            flash("Your password has been reset, you can log in.", "positive")
            return redirect(url_for("userfe.login"))

    return render_template("frontend/user/reset.html", form=form, token=token)
