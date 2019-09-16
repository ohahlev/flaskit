from sqlalchemy import (
    Table, Column, Integer, String, Boolean,
    ForeignKey, DateTime, or_, and_, text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from flask_login import UserMixin
from app import db, bcrypt, util
from sqlalchemy.sql import func


# between use and role
user_role = Table("user_role", db.Model.metadata,
                  Column("user_id", Integer, ForeignKey("user.id")),
                  Column("role_id", Integer, ForeignKey("role.id")))


class User(db.Model, UserMixin):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    phone = Column(String(32))
    email = Column(String(32))
    _password = Column(String(64))
    photo = Column(String(32))
    confirmed = Column(Boolean, default=False)
    deleted = Column(Boolean, default=False)

    token = Column(String(1024))

    date_created = Column(DateTime(timezone=False), server_default=func.now())
    last_updated = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    roles = relationship("Role", secondary=user_role, back_populates="users", order_by="Role.name")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext).decode('utf-8')

    def check_password(self, plaintext):
        return bcrypt.check_password_hash(self.password, plaintext)

    def get_id(self):
        return self.id

    def is_admin(self):
        role = next((x for x in self.roles if x.name == util.ADMIN), None)
        return role is not None

    @staticmethod
    def get_confirmeds():
        return [True, False]

    @staticmethod
    def get_deleteds():
        return [True, False]

    @staticmethod
    def search(empty, sorted_by, sorted_as, per_page, page, name_to_filter, email_to_filter,
               phone_to_filter):

        name_clause = or_(User.name.like("%{0}%".format(name_to_filter))).self_group()
        email_clause = or_(User.email.like("%{0}%".format(email_to_filter))).self_group()
        phone_clause = or_(User.phone.like("%{0}%".format(phone_to_filter))).self_group()

        clause_args = []

        if name_to_filter != empty:
            clause_args.append(name_clause)

        if email_to_filter != empty:
            clause_args.append(email_clause)

        if phone_to_filter != empty:
            clause_args.append(phone_clause)

        or_clause = or_(*clause_args)

        query = User.query.filter(or_clause).order_by(text("{0} {1}".format(sorted_by, sorted_as))) \
            .paginate(page, per_page, False)

        return query

    @staticmethod
    def advance_search(empty, sorted_by, sorted_as, per_page, page, id_to_filter, name_to_filter, email_to_filter,
                       phone_to_filter, confirmed_to_filter, deleted_to_filter, role_to_filter):

        roles = [x for x in Role.query.filter(Role.name.like("%{0}%".format(role_to_filter.upper()))).all()]
        users = []
        if len(roles) > 0:
            users = [x.users for x in roles][0]

        id_clause = and_(User.id == id_to_filter).self_group()
        name_clause = and_(User.name.like("%{0}%".format(name_to_filter))).self_group()
        email_clause = and_(User.email.like("%{0}%".format(email_to_filter))).self_group()
        phone_clause = and_(User.phone.like("%{0}%".format(phone_to_filter))).self_group()
        confirmed_clause = and_(User.confirmed == confirmed_to_filter).self_group()
        deleted_clause = and_(User.deleted == deleted_to_filter).self_group()
        role_clause = and_(User.id.in_([x.id for x in users])).self_group()

        clause_args = []

        if id_to_filter != empty:
            clause_args.append(id_clause)

        if name_to_filter != empty:
            clause_args.append(name_clause)

        if email_to_filter != empty:
            clause_args.append(email_clause)

        if phone_to_filter != empty:
            clause_args.append(phone_clause)

        if confirmed_to_filter != empty:
            clause_args.append(confirmed_clause)

        if deleted_to_filter != empty:
            clause_args.append(deleted_clause)

        if role_to_filter != empty:
            clause_args.append(role_clause)

        and_clause = and_(*clause_args)

        query = User.query.filter(and_clause).order_by(text("{0} {1}".format(sorted_by, sorted_as))) \
            .paginate(page, per_page, False)

        return query


class Role(db.Model):

    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    icon = Column(String(32))
    deleted = Column(Boolean, default=False)

    users = relationship("User", secondary=user_role, back_populates="roles")

    @staticmethod
    def list():
        return Role.query.order_by(Role.id.asc()).all()

