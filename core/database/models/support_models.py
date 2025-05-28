"""
МОдуль объявления таблиц необходимых для модерации доступов
"""
from sqlalchemy import Column, BigInteger, Integer

from .base import Base


class Admins(Base):
    """Администраторы"""
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    admin_id = Column(BigInteger)


class Judges(Base):
    """Судьи"""
    __tablename__ = 'judges'

    judge_id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
