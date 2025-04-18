from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
# from .main_models import Team

from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


class MatchStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class FootballMatch(Base):
    __tablename__ = 'football_matches'
    __table_args__ = {'extend_existing': True}

    match_id = Column(Integer, primary_key=True)
    team1_id = Column(Integer, ForeignKey('teams.team_id'))
    team2_id = Column(Integer, ForeignKey('teams.team_id'))
    group_name = Column(String(4))  # Группа (до 4 символов)
    score1 = Column(Integer, default=0)
    score2 = Column(Integer, default=0)

    status = Column(
        SQLAlchemyEnum(MatchStatus),
        nullable=False,
        default=MatchStatus.NOT_STARTED,
        server_default="NOT_STARTED"
    )
    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])
    # goals = relationship("FootballGoal", back_populates="match")
    goals = relationship(
        "FootballGoal",
        back_populates="match",
        cascade="all, delete-orphan",  # Автоматическое удаление голов при удалении матча
        passive_deletes=True
    )
    fallers = relationship(
        "FootballFallers",
        back_populates="match",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __str__(self):
        return (f'match_id: {self.match_id}, team1_id: {self.team1_id}, team2_id: {self.team2_id}, '
               f'group_name: {self.group_name}, score1: {self.score1}, score2: {self.score2}, ')


class FootballGoal(Base):
    __tablename__ = 'football_goals'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('football_matches.match_id'))
    scorer_id = Column(Integer, ForeignKey('participants.participant_id'))
    half = Column(Integer, nullable=False)  # 1 - первый тайм, 2 - второй тайм

    match = relationship("FootballMatch", back_populates="goals")
    scorer = relationship("Participant")


class FootballFallers(Base):
    __tablename__ = 'football_fallers'

    id = Column(Integer, primary_key=True)
    faller_id = Column(Integer, ForeignKey('participants.participant_id'))
    match_id = Column(Integer, ForeignKey('football_matches.match_id', ondelete="CASCADE"))

    # Связи
    faller = relationship(
        "Participant",
        back_populates="football_falls",  # Обратная ссылка в Participant
        lazy="joined"  # Опционально: автоматическая загрузка связанного участника
    )

    match = relationship(
        "FootballMatch",
        back_populates="fallers",  # Обратная ссылка в FootballMatch
        lazy="select"  # Стандартная ленивая загрузка
    )

    def __repr__(self):
        return f"<FootballFaller {self.id}: Participant {self.faller_id} in Match {self.match_id}>"


class FootballScores(Base):
    __tablename__ = 'football_scores'

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('football_matches.match_id'))
    team1_id = Column(Integer, ForeignKey('teams.team_id'))
    team2_id = Column(Integer, ForeignKey('teams.team_id'))
    score1 = Column(Integer, default=0)
    score2 = Column(Integer, default=0)
