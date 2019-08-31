from flask_script import Manager, prompt_bool, Shell, Server
from termcolor import colored
from app import app, db, util
from app.models import (
    User, Role
)

manager = Manager(app)


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


def create_role_data():
    role_admin = Role.query.filter_by(name=util.ADMIN).first()
    if not role_admin:
        role_admin = Role(name=util.ADMIN, icon="security")
        db.session.add(role_admin)

    role_user = Role.query.filter_by(name=util.USER).first()
    if not role_user:
        role_user = Role(name=util.USER, icon="person")
        db.session.add(role_user)


def create_user_data():
    admin_email = "admin@gmail.com"

    role_admin = Role.query.filter_by(name=util.ADMIN).first()
    if not role_admin:
        raise Exception("role admin not found in database")

    role_user = Role.query.filter_by(name=util.USER).first()
    if not role_user:
        raise Exception("role user not found in database")

    user_admin = User.query.filter_by(email=admin_email).first()
    if not user_admin:
        user_admin = User(
            name="admin",
            email=admin_email,
            password="ahlev",
            phone="123456",
            confirmed=True
        )
        user_admin.roles.append(role_admin)
        user_admin.roles.append(role_user)
        db.session.add(user_admin)

    for i in range(20):
        user = User.query.filter_by(email="{0}@gmail.com".format(i)).first()
        if not user:
            if i % 2 == 0:
                user = User(
                    name="user{0}".format(i),
                    email="{0}@gmail.com".format(i),
                    password="ahlev",
                    confirmed=True,
                    phone="{}".format(100 + i)
                )
            else:
                user = User(
                    name="user{0}".format(i),
                    email="{0}@gmail.com".format(i),
                    password="ahlev",
                    confirmed=False,
                    phone="{}".format(100 + i)
                )
            user.roles.append(role_user)
            if i < 10:
                user.roles.append(role_admin)
            db.session.add(user)


@manager.command
def init_data():
    create_role_data()
    create_user_data()
    db.session.commit()


manager.add_command("runserver", Server())
manager.add_command("shell", Shell(make_context=make_shell_context))

if __name__ == "__main__":
    manager.run()
