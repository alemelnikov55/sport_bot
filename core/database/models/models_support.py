"""
МОдуль объявления таблиц необходимых для модерации доступов
"""
from sqlalchemy import Column, BigInteger

from .base import Base


class Admins(Base):
    """Администраторы"""
    __tablename__ = 'admins'

    admin_id = Column(BigInteger, primary_key=True)


class Judges(Base):
    """Судьи"""
    __tablename__ = 'judges'

    judge_id = Column(BigInteger, primary_key=True)
