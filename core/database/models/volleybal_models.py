from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLAlchemyEnum

from .base import Base


class VolleyballMatchStatus(PyEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class VolleyballMatch(Base):
    __tablename__ = 'volleyball_matches'

    match_id = Column(Integer, primary_key=True)
    team1_id = Column(Integer, ForeignKey('teams.team_id'))
    team2_id = Column(Integer, ForeignKey('teams.team_id'))
    group_name = Column(String(4), nullable=True)
    status = Column(SQLAlchemyEnum(VolleyballMatchStatus), default=VolleyballMatchStatus.NOT_STARTED)

    # Счётчики побед в сетах
    team1_set_wins = Column(Integer, default=0, nullable=False)
    team2_set_wins = Column(Integer, default=0, nullable=False)

    # id победителя (может быть пустым если матч не завершён)
    winner_id = Column(Integer, ForeignKey('teams.team_id'), nullable=True)

    # Связи
    team1 = relationship("Team", foreign_keys=[team1_id])
    team2 = relationship("Team", foreign_keys=[team2_id])
    winner = relationship("Team", foreign_keys=[winner_id])
    sets = relationship(
        "VolleyballSet",
        back_populates="match",
        cascade="all, delete-orphan",
        order_by="VolleyballSet.set_number"
    )

    def __str__(self):
        return f"match_id:{self.match_id}\nteam1_id: {self.team1_id} - team2_id: {self.team2_id}\n{self.team1_set_wins} - {self.team2_set_wins}\n{self.status}"


class VolleyballSet(Base):
    __tablename__ = 'volleyball_sets'

    set_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('volleyball_matches.match_id'))
    set_number = Column(Integer)
    status = Column(SQLAlchemyEnum(VolleyballMatchStatus), default=VolleyballMatchStatus.NOT_STARTED)

    # Явные ссылки на команды
    team1_id = Column(Integer, ForeignKey('teams.team_id'))
    team2_id = Column(Integer, ForeignKey('teams.team_id'))

    team1_score = Column(Integer, default=0)
    team2_score = Column(Integer, default=0)

    match = relationship("VolleyballMatch", back_populates="sets")

    __table_args__ = (
        CheckConstraint('set_number BETWEEN 1 AND 3'),
    )

    def __str__(self):
        return (f"{self.match_id} - {self.set_number}\n"
                f"{self.team1_score} - {self.team2_score}\n{self.status}")

# Под удаление
    # @property
    # def winner(self) -> Optional[int]:
    #     """Возвращает 1 (team1), 2 (team2) или None если сет не завершён или ничья"""
    #     if self.status != VolleyballMatchStatus.FINISHED:
    #         return None
    #
    #     if self.team1_score > self.team2_score:
    #         return 1
    #     elif self.team2_score > self.team1_score:
    #         return 2
    #     return None  # Ничья (хотя в волейболе такого быть не должно)
