from sqlalchemy import (
    Column, Integer, String, DateTime
)
from sqlalchemy.sql import func
from app import db


class Contact(db.Model):

    __tablename__ = "contact"

    id = Column(Integer, primary_key=True)
    phone1 = Column(String(32))
    phone2 = Column(String(32))
    email = Column(String(32))

    date_created = Column(DateTime(timezone=False), server_default=func.now())
    last_updated = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    @staticmethod
    def first():
        return Contact.query.first()
