from sqlalchemy import (
    Column, Integer, String, Boolean
)
from sqlalchemy.orm import relationship
from app.models import user_role
from app import db


class Role(db.Model):

    __tablename__ = "role"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    icon = Column(String(32))
    deleted = Column(Boolean, default=False)

    users = relationship("User", secondary=user_role, back_populates="roles",
                         cascade="all,delete")

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon
        }

    @staticmethod
    def list():
        return Role.query.order_by(Role.id.asc()).all()
