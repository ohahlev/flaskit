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
from app.models import User, Role
from app.forms import user as user_forms
from app.toolbox import email

# Serializer for generating random tokens
ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])

# Create a user blueprint
bp = Blueprint("userfe", __name__, url_prefix="/user")


@bp.route("/register", methods=["GET", "POST"])
def register():

    # can not register if already logged in
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("sitefe.index"))

    form = user_forms.FormRegister()

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
        except Exception as err:
            logger.exception(err)
            flash("can not register at this moment", "negative")
            return redirect(url_for("userfe.register"))    

        subject = "Please confirm your email address."

        token = ts.dumps(user.email, salt="email-confirm-key")

        confirm_url = url_for("userfe.confirm", token=token, _external=True)

        html = render_template("frontend/email/confirm.html",
                               confirm_url=confirm_url)

        email.send(user.email, subject, html)

        flash("Check your emails to confirm your email address.", "positive")

        return redirect(url_for("userfe.login"))

    return render_template("frontend/user/register.html", form=form, title="Register")


@bp.route("/confirm/<token>", methods=["GET", "POST"])
def confirm(token):

    # can not confirm if already logged in
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("sitefe.index"))

    email = None

    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)

    except:
        abort(404)

    # Get the user from the database
    user = User.query.filter_by(email=email).first()
    
    # The user has confirmed his or her email address
    user.confirmed = True
    
    # Update the database with the user
    try:
        db.session.commit()
    except Exception as err:
        logger.exception(err)
        flash("can not confirm email at this moment", "negative")
        return redirect(url_for("userfe.confirm", token=token))

    # Send to the login page
    flash("Your email address has been confirmed, you can log in.", "positive")
    return redirect(url_for("userfe.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():

    # redirect to home if already logged
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("sitefe.index"))

    form = user_forms.FormLogin()

    next_page = ""

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        # check if user exists
        if user is None:
            flash("Unknown email address.", "negative")
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
            flash("The password you have entered is wrong.", "negative")
            return redirect(url_for("userfe.login"))

        # everything is good to go

        login_user(user)
        flash("Succesfully logged in.", "positive")

        # send back to previous attempt
        next_page = form.next.data
        if next_page:
            resp = make_response(redirect(next_page))
        else:
            resp = make_response(redirect(url_for("sitefe.index")))

        resp.set_cookie("user", value=user.email)
        return resp
            
    return render_template("frontend/user/login.html", form=form, title="Log in", next=next_page)


@bp.route("/logout")
def logout():

    # can not logout if not yet logged in
    if request.method == "GET" and current_user.is_authenticated == False:
        return redirect(url_for("sitefe.index"))
    logout_user()
    resp = make_response(redirect(url_for("sitefe.index")))
    resp.set_cookie("user", "", expires=0)
    flash("Succesfully logout out.", "positive")
    return resp


@bp.route("/profile/<int:id>", methods=["GET", "POST"])
@login_required
def profile(id):
    
    form_edit_profile = user_forms.FormEditProfile()
    form_change_password = user_forms.FormChangePassword()
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

    form = user_forms.FormForgot()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # Check the user exists
        if user is not None:
            # Subject of the confirmation email
            subject = "Reset your password."
            # Generate a random token
            token = ts.dumps(user.email, salt="password-reset-key")
            # Build a reset link with token
            resetUrl = url_for("userfe.reset", token=token, _external=True)
            # Render an HTML template to send by email
            html = render_template("frontend/email/reset.html", reset_url=resetUrl)
            # Send the email to user
            email.send(user.email, subject, html)
            # Send back to the home page
            flash("Check your emails to reset your password.", "positive")
            return redirect(url_for("sitefe.index"))
        else:
            flash("Unknown email address.", "negative")
            return redirect(url_for("userfe.forgot"))
    return render_template("frontend/user/forgot.html", form=form)


@bp.route("/reset/<token>", methods=["GET", "POST"])
def reset(token):

    # can not reset if already logged in
    if request.method == "GET" and current_user.is_authenticated:
        return redirect(url_for("sitefe.index"))

    email = None

    try:
        email = ts.loads(token, salt="password-reset-key", max_age=86400)
    # The token can either expire or be invalid
    except:
        abort(404)

    form = user_forms.FormReset()
    if form.validate_on_submit():
        
        user = User.query.filter_by(email=email).first()
        # Check the user exists
        if user is not None:
            user.password = form.password.data.strip()
            
            # Update the database with the user
            try:
                db.session.commit()
            except Exception as err:
                logger.exception(err)
                flash("can not reset password at this moment", "negative")
                return redirect(url_for("userfe.reset", token=token))
            
            # Send to the login page
            flash("Your password has been reset, you can log in.", "positive")
            return redirect(url_for("userfe.login"))
        else:
            flash("Unknown email address.", "negative")
            return redirect(url_for("userfe.forgot"))
    return render_template("frontend/user/reset.html", form=form, token=token)
