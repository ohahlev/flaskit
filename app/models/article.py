from sqlalchemy import (
    Column, Integer, String, DateTime, Text
)
from sqlalchemy.sql import func
from app import db, util


class Article(db.Model):

    __tablename__ = "article"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    type = Column(String(32))

    date_created = Column(DateTime(timezone=False), server_default=func.now())
    last_updated = Column(DateTime(timezone=False), server_default=func.now(), onupdate=func.now())

    @staticmethod
    def list():
        return Article.query.order_by(Article.last_updated.desc()).all()

    @staticmethod
    def find_about():
        return Article.query.filter_by(type=util.ABOUT).first()

    @staticmethod
    def find_contact():
        return Article.query.filter_by(type=util.CONTACT).first()
