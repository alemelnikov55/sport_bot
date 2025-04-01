from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base
from .main_models import Team


class FootballMatch(Base):
    __tablename__ = 'football_matches'
    __table_args__ = {'extend_existing': True}

    match_id = Column(Integer, primary_key=True)
    team1_id = Column(Integer, ForeignKey('teams.team_id'))
    team2_id = Column(Integer, ForeignKey('teams.team_id'))
    group_name = Column(String(4))  # Группа (до 4 символов)
    score1 = Column(Integer, default=0)
    score2 = Column(Integer, default=0)

    status = Column(String(20))  # SCHEDULED, IN_PROGRESS, FINISHED

    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])
    goals = relationship("FootballGoal", back_populates="match")


class FootballGoal(Base):
    __tablename__ = 'football_goals'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('football_matches.match_id'))
    scorer_id = Column(Integer, ForeignKey('participants.participant_id'))
    half = Column(Integer, nullable=False)  # 1 - первый тайм, 2 - второй тайм

    match = relationship("FootballMatch", back_populates="goals")
    scorer = relationship("Participant")
