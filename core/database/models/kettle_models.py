"""
Модель для хранения результатов гиревого спорта
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, func, String

from database.models import Base


class KettleResult(Base):
    __tablename__ = 'kettle_results'

    result_id = Column(Integer, primary_key=True)
    lifter_id = Column(Integer, ForeignKey('participants.participant_id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    category = Column(String, nullable=True)
    lift_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    judge_id = Column(Integer, ForeignKey('judges.judge_id'), nullable=False)
