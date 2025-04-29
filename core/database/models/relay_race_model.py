"""
Модель для хранения результатов эстафетного бега
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, func

from database.models import Base


class RelayResult(Base):
    __tablename__ = 'relay_results'

    result_id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
    result_time = Column(Numeric(6, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    judge_id = Column(Integer, ForeignKey('judges.judge_id'), nullable=False)

    def __str__(self):
        return (f'<RelayResult> result_id: {self.result_id} team_id: {self.team_id} result_time: {self.result_time}'
                f'timestamp: {self.timestamp} judge_id: {self.judge_id}')