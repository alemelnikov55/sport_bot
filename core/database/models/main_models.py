from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Sport(Base):
    __tablename__ = 'sports'

    sport_id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    is_team = Column(Boolean, default=False)
    gender_specific = Column(Boolean, default=False)


class Team(Base):
    __tablename__ = 'teams'

    team_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    participants = relationship("Participant", back_populates="team")


class Participant(Base):
    __tablename__ = 'participants'

    participant_id = Column(Integer, primary_key=True)
    full_name = Column(String(150), nullable=False)
    short_name = Column(String(50), nullable=False)
    gender = Column(String(1), nullable=False)  # M or F
    age = Column(Integer, nullable=False)

    team_id = Column(Integer, ForeignKey('teams.team_id'))

    team = relationship("Team", back_populates="participants")
    sports = relationship("ParticipantSport", back_populates="participant")
    football_falls = relationship("FootballFallers", back_populates="faller")

    def __str__(self):
        return (f'participant: {self.participant_id}, full name: {self.full_name}, gender: {self.gender}'
                f'age: {self.age}, team: {self.team_id}')


class ParticipantSport(Base):
    __tablename__ = 'participant_sports'

    participant_id = Column(Integer, ForeignKey('participants.participant_id'), primary_key=True)
    sport_id = Column(Integer, ForeignKey('sports.sport_id'), primary_key=True)

    participant = relationship("Participant", back_populates="sports")
    sport = relationship("Sport")