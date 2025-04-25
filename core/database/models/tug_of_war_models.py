from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


class TugStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class TugOfWarMatch(Base):
    __tablename__ = 'tug_of_war_matches'
    # __table_args__ = {'extend_existing': True}

    pull_id = Column(Integer, primary_key=True)
    team1_id = Column(Integer, ForeignKey('teams.team_id'))
    team2_id = Column(Integer, ForeignKey('teams.team_id'))
    group_name = Column(String(4))  # Группа (до 4 символов)
    score1 = Column(Integer, default=0)
    score2 = Column(Integer, default=0)

    status = Column(
        SQLAlchemyEnum(TugStatus),
        nullable=False,
        default=TugStatus.NOT_STARTED,
        server_default="NOT_STARTED"
    )

    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])

    def __str__(self):
        return (f'TugOfWarMatch id: pull_id: {self.pull_id} team1: {self.team1} team2: {self.team2} status: {self.status}'
                f'group_name: {self.group_name} score1: {self.score1} score2: {self.score2}')