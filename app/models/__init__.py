from sqlalchemy import (
    Table, Column, Integer, ForeignKey
)
from app import db

# between use and role
user_role = Table("user_role", db.Model.metadata,
                  Column("user_id", Integer, ForeignKey("user.id")),
                  Column("role_id", Integer, ForeignKey("role.id")))
