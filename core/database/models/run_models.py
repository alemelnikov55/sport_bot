"""
Модель для хранения результатов бега
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, func

from database.models import Base


class RunningResult(Base):
    __tablename__ = 'running_results'

    result_id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('participants.participant_id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    distance_m = Column(Integer, nullable=False)
    result_time = Column(Numeric(6, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    judge_id = Column(Integer, ForeignKey('judges.judge_id'), nullable=False)
