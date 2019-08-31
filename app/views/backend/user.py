import os
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, jsonify, redirect, url_for,
    flash, abort, make_response, request
)

from sqlalchemy.orm import lazyload
from app import app, db, logger, util
from app.models import User, Role
from app.forms.user import (
    FormCreateUser, FormEditProfileForAdmin
)
from app.util import role_required, ADMIN, USER

bp = Blueprint("userbe", __name__, url_prefix="/backend/users")


@bp.route("/", methods=["GET"])
@role_required([ADMIN])
def index():

    return redirect(url_for("userbe.search_users_results", is_advanced=0, keyword=util.EMPTY,
                            sorted_by=util.DEFAULT_SORT, sorted_as="desc", per_page=util.PER_PAGE, page=1,
                            id_to_filter=util.EMPTY, name_to_filter=util.EMPTY,
                            email_to_filter=util.EMPTY, phone_to_filter=util.EMPTY, confirmed_to_filter=util.EMPTY,
                            deleted_to_filter=util.EMPTY, role_to_filter=util.EMPTY))


@bp.route("/delete/<int:id>", methods=["POST"])
@role_required([ADMIN])
def delete_user(id):

    user = User.query.filter_by(id=id).first()
    if not user:
        abort(make_response(jsonify(message="user with name = {0} is not found".format(user.name))), 404)

    try:
        if user.deleted:
            user.deleted = False
        else:
            user.deleted = True
        db.session.commit()
    except Exception as err:
        logger.exception(err)
        abort(make_response(jsonify(message="can not remove user with name = {0}".format(user.name))), 500)
    
    if not user.deleted:
        return "user with name = {0} comes back".format(user.name)

    return "user with name = {0} is removed".format(user.name)


@bp.route("/create", methods=["GET", "POST"])
@role_required([ADMIN])
def create_user():

    form = FormCreateUser()
    
    roles = Role.query.all()
    user_role = next((x for x in roles if x.name == USER), None)

    if form.validate_on_submit():

        user = User(
            name=form.name.data.strip(),
            phone=form.phone.data.strip(),
            email=form.email.data.strip(),
            password=form.password.data.strip(),
            confirmed=True
        )

        # assign role as normal user
        
        role_ids = zip(request.form.getlist("roles"))
        found_user_role = False
        for role_id in role_ids:
            find_role = next((x for x in roles if x.id == int(role_id[0])), None)
            if find_role:
                user.roles.append(find_role)
            if find_role.id == user_role:
                found_user_role = True

        if found_user_role is False:
            user.roles.append(user_role)

        # validate photo upload extension
        file_name = None
        if form.photo.data:
            file_name = secure_filename(form.photo.data.filename)
        if file_name and not util.allowed_file(file_name, app.config["ALLOWED_EXTENSIONS"]):
            flash("photo upload allows only {}".format(",".join(app.config["ALLOWED_EXTENSIONS"])))
            return redirect(url_for("userbe.create_user"))
        
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as err:
            logger.exception(err)
            flash("can not create user at this moment", "negative")
            return redirect(url_for("userbe.create_user"))

        if file_name:
                
            # check if parent dir exist
            parent_dir = os.path.join("app", app.config["UPLOAD_FOLDER"], 
                    "users", "{}".format(user.id), "photo")
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            # if file for new logo already exists
            new_logo = os.path.join(parent_dir, "{0}".format(file_name))
            if os.path.isfile(new_logo):
                os.remove(new_logo)

            # save new logo to file
            form.photo.data.save(new_logo)

            user.photo = file_name

            try:
                db.session.commit()
            except Exception as err:
                logger.exception(err)
                flash("can not create user at this moment", "negative")
                return redirect(url_for("userbe.create_user"))

        flash("user = {0} is created".format(user.name), "positive")

        return redirect(url_for("userbe.search_users_results", is_advanced=0, keyword=util.EMPTY,
                                sorted_by=util.DEFAULT_SORT, sorted_as="desc", per_page=10, page=1,
                                id_to_filter=util.EMPTY, name_to_filter=util.EMPTY, email_to_filter=util.EMPTY,
                                phone_to_filter=util.EMPTY, confirmed_to_filter=util.EMPTY,
                                deleted_to_filter=util.EMPTY, role_to_filter=util.EMPTY))

    return render_template("backend/user/create.html", title="Create User", form=form, roles=roles, user_role=user_role)

    
@bp.route("/edit/<int:id>", methods=["GET", "POST"])
@role_required([ADMIN])
def edit_user(id):
    
    user = User.query.options(lazyload(User.roles)).filter_by(id=id).first()
    if not user:
        abort(404)

    roles = Role.query.all()
    user_role = next((x for x in roles if x.name == USER), None)
    
    form = FormEditProfileForAdmin()

    if request.method == "GET":
        form.name.data = user.name
        form.phone.data = user.phone
        form.email.data = user.email

    if form.validate_on_submit():

        # validate photo upload extension
        file_name = None
        if form.photo.data:
            file_name = secure_filename(form.photo.data.filename)
        if file_name and not util.allowed_file(file_name, app.config["ALLOWED_EXTENSIONS"]):
            flash("photo upload allows only {}".format(",".join(app.config["ALLOWED_EXTENSIONS"])))
            return redirect(url_for("userbe.edit_user", id=user.id))

        # properties setter
        changed = False
        if user.name != form.name.data.strip():
            user.name = form.name.data.strip()
            changed = True

        if form.phone.data and user.phone != form.phone.data.strip():
            user.phone = form.phone.data.strip()
            changed = True

        if form.password.data and user.check_password(form.password.data.strip()) is False:
            user.password = form.password.data.strip()
            changed = True
            
        role_ids = request.form.getlist("roles")

        not_user_roles = []
        for role_id in role_ids:
            print("given role id = {0}, user_role.id = {1}".format(role_id, user_role.id))
            if int(role_id) != user_role.id:
                find_role = next((x for x in roles if x.id == int(role_id)), None)
                if find_role:
                    not_user_roles.append(find_role)

        for not_user_role in not_user_roles:
            find_role = next((x for x in user.roles if x.id == not_user_role.id and x.id != user_role.id), None)
            if find_role is None:
                user.roles.append(not_user_role)
                changed = True

        for role in user.roles:
            if role.id != user_role.id:
                find_role = next((x for x in not_user_roles if x.id == role.id), None)
                if find_role is None:
                    user.roles.remove(role)
                    changed = True

        if changed is True:
            try:
                db.session.commit()
            except Exception as err:
                logger.exception(err)
                flash("can not edit user by name = {}".format(user.name), "negative")
                return redirect(url_for("userbe.edit_user", id=id))

        if file_name and file_name != user.photo:

            changed = True
                
            # check if parent dir exist
            parent_dir = os.path.join("app", app.config["UPLOAD_FOLDER"], "users", "{}".format(user.id), "photo")
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)

            # remove current photo
            current_photo = os.path.join(parent_dir, "{0}".format(user.photo))
            if os.path.isfile(current_photo):
                os.remove(current_photo)
            
            # if file for new photo already exists
            new_photo = os.path.join(parent_dir, "{0}".format(file_name))
            if os.path.isfile(new_photo):
                os.remove(new_photo)

            # save new logo to file
            form.photo.data.save(new_photo)

            user.photo = file_name
            db.session.commit()
                
        if changed is False:
            flash("data is not changed", "negative")
            return redirect(url_for("userbe.edit_user", id=id))
        else:
            flash("user by name = {0} is updated".format(user.name), "positive")

            return redirect(url_for("userbe.search_users_results", is_advanced=0, keyword=util.EMPTY,
                                    sorted_by=util.DEFAULT_SORT, sorted_as="desc", per_page=10, page=1,
                                    id_to_filter=util.EMPTY, name_to_filter=util.EMPTY, email_to_filter=util.EMPTY,
                                    phone_to_filter=util.EMPTY, confirmed_to_filter=util.EMPTY,
                                    deleted_to_filter=util.EMPTY, role_to_filter=util.EMPTY))
        
    return render_template("backend/user/edit.html", title="Edit User", form=form,
                           roles=roles, user=user, user_role=user_role)


@bp.route("/search", methods=["POST"])
@role_required([ADMIN])
def search_users():
    
    sorted_by = request.form["sorted_by"]
    sorted_as = request.form["sorted_as"]

    keyword = request.form["keyword"]
    if keyword == "":
        name_to_filter = request.form["name_to_filter"] if request.form["name_to_filter"] != "" else util.EMPTY
        email_to_filter = request.form["email_to_filter"] if request.form["email_to_filter"] != "" else util.EMPTY
        phone_to_filter = request.form["phone_to_filter"] if request.form["phone_to_filter"] != "" else util.EMPTY
        role_to_filter = request.form["role_to_filter"] if request.form["role_to_filter"] != "" else util.EMPTY
        keyword = util.EMPTY
    else:
        name_to_filter = keyword
        email_to_filter = keyword
        phone_to_filter = keyword
        role_to_filter = keyword
    
    return redirect(url_for("userbe.search_users_results", is_advanced=0, keyword=keyword, sorted_by=sorted_by,
                            sorted_as=sorted_as, per_page=util.PER_PAGE, page=1, id_to_filter=util.EMPTY,
                            name_to_filter=name_to_filter, email_to_filter=email_to_filter,
                            phone_to_filter=phone_to_filter, confirmed_to_filter=util.EMPTY,
                            deleted_to_filter=util.EMPTY, role_to_filter=role_to_filter))


@bp.route("/search/advance", methods=["POST"])
@role_required([ADMIN])
def advance_search_users():
    
    sorted_by = request.form["sorted_by"]
    sorted_as = request.form["sorted_as"]

    id_to_filter = request.form["id_to_filter"] if request.form["id_to_filter"] != "" else util.EMPTY 
    name_to_filter = request.form["name_to_filter"] if request.form["name_to_filter"] != "" else util.EMPTY
    email_to_filter = request.form["email_to_filter"] if request.form["email_to_filter"] != "" else util.EMPTY
    phone_to_filter = request.form["phone_to_filter"] if request.form["phone_to_filter"] != "" else util.EMPTY
    confirmed_to_filter = request.form["confirmed_to_filter"] if request.form["confirmed_to_filter"] != "" else util.EMPTY
    deleted_to_filter = request.form["deleted_to_filter"] if request.form["deleted_to_filter"] != "" else util.EMPTY
    role_to_filter = request.form["role_to_filter"] if request.form["role_to_filter"] != "" else util.EMPTY
    
    return redirect(url_for("userbe.search_users_results", is_advanced=1, keyword=util.EMPTY, sorted_by=sorted_by,
                            sorted_as=sorted_as, per_page=util.PER_PAGE, page=1, id_to_filter=id_to_filter,
                            name_to_filter=name_to_filter, email_to_filter=email_to_filter,
                            phone_to_filter=phone_to_filter, confirmed_to_filter=confirmed_to_filter,
                            deleted_to_filter=deleted_to_filter, role_to_filter=role_to_filter))


@bp.route("/search?is_advanced=<int:is_advanced>&keyword=<keyword>&sorted_by=<sorted_by>&sorted_as=<sorted_as>"
          "&per_page=<int:per_page>&page=<int:page>&filtered_by_id=<id_to_filter>&filtered_by_name=<name_to_filter>"
          "&filtered_by_email=<email_to_filter>&filtered_by_phone=<phone_to_filter>"
          "&filtered_by_confirmed=<confirmed_to_filter>&filtered_by_deleted=<deleted_to_filter>"
          "&filtered_by_role=<role_to_filter>", methods=["GET", "POST"])
@role_required([ADMIN])
def search_users_results(is_advanced, keyword, sorted_by, sorted_as, per_page, page, id_to_filter, name_to_filter,
                         email_to_filter, phone_to_filter, confirmed_to_filter, deleted_to_filter, role_to_filter):

    if is_advanced == 1:
        query = User.advance_search(util.EMPTY, sorted_by, sorted_as, per_page, page, id_to_filter, name_to_filter,
                                    email_to_filter, phone_to_filter, confirmed_to_filter, deleted_to_filter,
                                    role_to_filter)
    else:
        query = User.search(util.EMPTY, sorted_by, sorted_as, per_page, page, name_to_filter,
                            email_to_filter, phone_to_filter)
    
    users = query.items
    total = query.total

    if total % per_page == 0:
        last_page = int(total/per_page)
    elif total % per_page > 0:
        last_page = int(total/per_page) + 1

    confirmeds = User.get_confirmeds()
    deleteds = User.get_deleteds()

    roles = Role.list()

    return render_template("backend/user/search.html", title="Search Result", users=users, empty_hash=util.EMPTY,
                           per_page=per_page, page=page, total=total, last_page=last_page, confirmeds=confirmeds,
                           deleteds=deleteds, roles=roles, sorted_by=sorted_by, sorted_as=sorted_as,
                           id_to_filter=id_to_filter, name_to_filter=name_to_filter, keyword=keyword,
                           email_to_filter=email_to_filter, phone_to_filter=phone_to_filter,
                           confirmed_to_filter=confirmed_to_filter, deleted_to_filter=deleted_to_filter,
                           role_to_filter=role_to_filter, is_advanced=is_advanced)


@bp.route("/add/user/place", methods=["POST"])
@role_required([ADMIN])
def add_place():
    user_id = request.form.get("user_id")
    place_id = request.form.get("place_id")

    user = User.find_by_id(user_id)
    if not user:
        abort(404)

    place = Place.find_by_id(place_id)
    if not place:
        abort(404)

    place.user = user

    try:
        db.session.commit()
        flash("{0} is added to user {1}".format(place.name, user.name), "positive")
    except Exception as err:
        logger.exception(err)
        flash("can not add {0} to user {1} at this moment".format(place.name, user.name),
              "negative")

    return redirect(url_for("userbe.edit_user", id=user.id))


@bp.route("/delete/user/place/<int:id>", methods=["GET", "POST"])
@role_required([ADMIN])
def delete_place(id):

    place = Place.find_by_id(id)

    if not place:
        abort(404)

    user_id = place.user.id
    place.user = None

    try:
        db.session.commit()
        flash("{0} is unlinked".format(place.name), "positive")
    except Exception as err:
        logger.exception(err)
        flash("can not unlink place {0}".format(place.name), "negative")

    return redirect(url_for("userbe.edit_user", id=user_id))




