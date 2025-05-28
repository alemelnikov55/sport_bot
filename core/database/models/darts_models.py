from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from .base import Base

from sqlalchemy import Enum as SQLAlchemyEnum


class DartsPlayoffType(PyEnum):
    ONE_EIGHTH = "1/8 финала"
    ONE_QUARTER = "1/4 финала"
    ONE_HALF = "1/2 финала"
    FINAL = "финал"
    THIRD_PLACE = "3-е место"

    @classmethod
    def get_data_for_chose_type(cls):
        data = [
            {'type_value': cls.ONE_EIGHTH, 'name': cls.ONE_EIGHTH.value, 'id': cls.ONE_EIGHTH.name},
            {'type_value': cls.ONE_QUARTER, 'name': cls.ONE_QUARTER.value, 'id': cls.ONE_QUARTER.name},
            {'type_value': cls.ONE_HALF, 'name': cls.ONE_HALF.value, 'id': cls.ONE_HALF.name},
            {'type_value': cls.THIRD_PLACE, 'name': cls.THIRD_PLACE.value, 'id': cls.THIRD_PLACE.name},
            {'type_value': cls.FINAL, 'name': cls.FINAL.value, 'id': cls.FINAL.name}
        ]
        return data

    # @classmethod



class DartsQualifiers(Base):
    __tablename__ = 'darts_qualifiers'

    qualifiers_id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('participants.participant_id'))
    team_id = Column(Integer, ForeignKey('teams.team_id'))
    score = Column(Integer, nullable=False)  # Очки, набранные игроком в раунде
    timestamp = Column(DateTime, nullable=False, default=func.now())
    judge_id = Column(Integer, ForeignKey('judges.judge_id'), nullable=False)

    def __str__(self):
        return (f"Qualifiers {self.qualifiers_id}: Player {self.player_id} "
                f"from Team {self.team_id} with score {self.score}")


class DartsPlayOff(Base):
    __tablename__ = 'darts_playoffs'

    playoff_id = Column(Integer, primary_key=True)
    player1_id = Column(Integer, ForeignKey('participants.participant_id'))
    player2_id = Column(Integer, ForeignKey('participants.participant_id'))
    playoff_type = Column(SQLAlchemyEnum(DartsPlayoffType), nullable=False)

    player1_wins = Column(Integer, default=0, nullable=False)
    player2_wins = Column(Integer, default=0, nullable=False)

    winner_id = Column(Integer, ForeignKey('participants.participant_id'), nullable=True)

    def __str__(self):
        return (f"Playoff {self.playoff_id}: {self.player1_id} vs {self.player2_id}\n"
                f"Wins: {self.player1_wins}-{self.player2_wins}\n"
                f"Type: {self.playoff_type}")
