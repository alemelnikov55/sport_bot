from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, ForeignKey, String, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLAlchemyEnum

from .base import Base


class PongMatchStatus(PyEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


class TableTennisMatch(Base):
    __tablename__ = 'table_tennis_matches'

    match_id = Column(Integer, primary_key=True)
    player1_id = Column(Integer, ForeignKey('participants.participant_id'))  # Участник 1
    player2_id = Column(Integer, ForeignKey('participants.participant_id'))  # Участник 2
    group_name = Column(String(4), nullable=True)  # Группа (если есть)
    status = Column(SQLAlchemyEnum(PongMatchStatus), default=PongMatchStatus.NOT_STARTED)

    # Счётчики побед в сетах (игра до 2 побед)
    player1_set_wins = Column(Integer, default=0, nullable=False)
    player2_set_wins = Column(Integer, default=0, nullable=False)

    # ID победителя (участника)
    winner_id = Column(Integer, ForeignKey('participants.participant_id'), nullable=True)

    # Связи
    player1 = relationship("Participant", foreign_keys=[player1_id])
    player2 = relationship("Participant", foreign_keys=[player2_id])
    winner = relationship("Participant", foreign_keys=[winner_id])
    sets = relationship(
        "TableTennisSet",
        back_populates="match",
        cascade="all, delete-orphan",
        order_by="TableTennisSet.set_number"
    )

    def __str__(self):
        return (f"Match {self.match_id}: {self.player1_id} vs {self.player2_id}\n"
                f"Sets: {self.player1_set_wins}-{self.player2_set_wins}\n"
                f"Status: {self.status}")


class TableTennisSet(Base):
    __tablename__ = 'table_tennis_sets'

    set_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('table_tennis_matches.match_id'))
    set_number = Column(Integer)  # Номер сета (1, 2 или 3)
    status = Column(SQLAlchemyEnum(PongMatchStatus), default=PongMatchStatus.NOT_STARTED)

    # Ссылки на участников (дублируем для удобства)
    player1_id = Column(Integer, ForeignKey('participants.participant_id'))
    player2_id = Column(Integer, ForeignKey('participants.participant_id'))

    player1_score = Column(Integer, default=0)
    player2_score = Column(Integer, default=0)

    match = relationship("TableTennisMatch", back_populates="sets")

    __table_args__ = (
        CheckConstraint('set_number BETWEEN 1 AND 3'),
    )

    def __str__(self):
        return (f"Set {self.set_number} (Match {self.match_id})\n"
                f"Score: {self.player1_score}-{self.player2_score}\n"
                f"Status: {self.status}")
