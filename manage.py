import os
import json
from flask_script import Manager, prompt_bool, Shell, Server
from termcolor import colored
from app import app, db, util
from app.models.user import User
from app.models.role import Role
from app.models.article import Article
from app.models.contact import Contact

manager = Manager(app)

admin_email = "ohahlev@gmail.com"
admin_contact_number = "1234567"

def make_shell_context():
    return dict(app=app)


@manager.command
def init_db():
    db.create_all()
    print(colored("The SQL database has been created", "green"))


@manager.command
def drop_db():
    if prompt_bool("Are you sure you want to lose all your SQL data?"):
        db.drop_all()
        print(colored("The SQL database has been deleted", "green"))


def init_article_data():
    about_us = Article.query.filter_by(type=util.ABOUT).first()
    if not about_us:
        about_us = Article(
            type=util.ABOUT,
            text="This is about us text paragraph",
        )
        db.session.add(about_us)

    contact_us = Article.query.filter_by(type=util.CONTACT).first()
    if not contact_us:
        contact_us = Article(
            type=util.CONTACT,
            text="This is contact us text paragraphe"
        )
        db.session.add(contact_us)

    contact = Contact.query.filter_by(phone1=admin_contact_number).first()
    if not contact:
        contact = Contact(
            phone1=admin_contact_number,
            email="asdfsadf@asfasdf.com"
        )
        db.session.add(contact)


def init_role_data():
    f = open(os.path.join("app", "static", "data", "roles.json"), "r+")
    content = f.read()
    f.close()
    jsonifieds = json.loads(content)
    for item in jsonifieds:
        name = item["name"]
        icon = item["icon"]
        role = Role.query.filter_by(name=name).first()
        if role is None:
            role = Role(name=name, icon=icon)
            db.session.add(role)
    db.session.commit()


def init_user_data():

    role_api = Role.query.filter_by(name=util.API).first()
    if not role_api:
        raise Exception("role = {0} is not found".format(util.API))

    role_admin = Role.query.filter_by(name=util.ADMIN).first()
    if not role_admin:
        raise Exception("role = {0} is not found".format(util.ADMIN))

    role_user = Role.query.filter_by(name=util.USER).first()
    if not role_user:
        raise Exception("role = {0} is not found".format(util.USER))

    api_user = User.query.filter_by(email=util.API_EMAIL).first()
    if not api_user:
        api_user = User(
            name=util.API,
            email=util.API_EMAIL,
            password=util.API_PASSWORD,
            confirmed=True
        )
        api_user.roles.append(role_user)
        api_user.roles.append(role_api)
        db.session.add(api_user)

    user_admin = User.query.filter_by(email=admin_email).first()
    if not user_admin:
        user_admin = User(
            name="admin",
            email=admin_email,
            password="malinka",
            confirmed=True,
            deleted=False,
            phone="123456",
        )
        user_admin.roles.append(role_user)
        user_admin.roles.append(role_admin)
        db.session.add(user_admin)

    for i in range(30):
        user = User.query.filter_by(email="{0}@gmail.com".format(i)).first()
        if not user:
            if i % 2 == 0:
                user = User(
                    name="user{0}".format(i),
                    email="{0}@gmail.com".format(i),
                    password="malinka",
                    confirmed=True,
                    deleted=False,
                    phone="{}".format(100 + i)
                )
            else:
                user = User(
                    name="user{0}".format(i),
                    email="{0}@gmail.com".format(i),
                    password="malinka",
                    confirmed=False,
                    deleted=True,
                    phone="{}".format(100 + i)
                )
            user.roles.append(role_user)
            db.session.add(user)

    db.session.commit()


@manager.command
def init_data():
    init_article_data()
    init_role_data()
    init_user_data()
    db.session.commit()


manager.add_command("runserver", Server())
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == "__main__":
    manager.run()
