"""
Модель для хранения результатов гиревого спорта
"""
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, func, String
from sqlalchemy import Enum as SQLAlchemyEnum

from database.models import Base


class KettleCategory(PyEnum):
    female_none = 'female_none'
    male_50 = 'male_50'
    male_51_60 = 'male_51_60'
    male_60_plus = 'male_60_plus'


class KettleResult(Base):
    __tablename__ = 'kettle_results'

    result_id = Column(Integer, primary_key=True)
    lifter_id = Column(Integer, ForeignKey('participants.participant_id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    category = Column(String, nullable=True)
    lift_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    judge_id = Column(Integer, ForeignKey('judges.judge_id'), nullable=False)
