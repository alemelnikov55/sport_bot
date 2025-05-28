from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class ExternalTeamMapping(Base):
    __tablename__ = 'external_team_mapping'

    # id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False, unique=True, primary_key=True)
    external_id = Column(String(100), nullable=False, unique=True)

    team = relationship("Team")


class ExternalSportMapping(Base):
    __tablename__ = 'external_sport_mapping'

    # id = Column(Integer, primary_key=True)
    sport_id = Column(Integer, ForeignKey('sports.sport_id'), nullable=False, unique=True, primary_key=True)
    external_id = Column(String(100), nullable=False, unique=True)

    sport = relationship("Sport")
