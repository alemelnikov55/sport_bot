# from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint, Table
# from sqlalchemy.orm import relationship
# from sqlalchemy.orm import declarative_base
#
# Base = declarative_base()
#
# # class FootballTeam(Base):
# #     __tablename__ = 'football_teams'
# #     team_id = Column(Integer, primary_key=True)
# #     name = Column(String(100), nullable=False, unique=True)
# #
# #     participants = relationship("TournamentParticipant", back_populates="football_team")
# #
# #     def __repr__(self):
# #         return f"<FootballTeam(id={self.team_id}, name='{self.name}')>"
# #
# #
# # class TournamentParticipant(Base):
# #     __tablename__ = 'tournament_participants'
# #
# #     participant_id = Column(Integer, primary_key=True)
# #     full_name = Column(String(150), nullable=False)  # Полное ФИО
# #     short_name = Column(String(50), nullable=False)  # Краткое имя (например, "Иванов И.")
# #     gender = Column(String(1), nullable=False)  # 'M' или 'F'
# #     age = Column(Integer, nullable=False)  # Возраст в годах
# #     football_team_id = Column(Integer, ForeignKey('football_teams.team_id'))
# #
# #     # Виды спорта
# #     plays_football = Column(Boolean, default=False)
# #     plays_volleyball = Column(Boolean, default=False)
# #
# #     # Связи
# #     football_team = relationship("FootballTeam", back_populates="participants")
# #     goals = relationship("FootballGoal", back_populates="participant")
# #
# #     __table_args__ = (
# #         CheckConstraint("gender IN ('M', 'F')", name='check_gender_values'),
# #         CheckConstraint("age > 0", name='check_age_positive')
# #     )
# #
# #     def __repr__(self):
# #         return f"<Participant(id={self.participant_id}, name='{self.short_name}')>"
#
# # Таблица связи многие-ко-многим для участников и видов спорта
# participant_sport = Table(
#     'participant_sport',
#     Base.metadata,
#     Column('participant_id', Integer, ForeignKey('tournament_participants.participant_id'), primary_key=True),
#     Column('sport_id', Integer, ForeignKey('sports.sport_id'), primary_key=True)
# )
#
#
# class Sport(Base):
#     """Виды спорта"""
#     __tablename__ = 'sports'
#
#     sport_id = Column(Integer, primary_key=True)
#     name = Column(String(50), nullable=False, unique=True)
#     is_team_sport = Column(Boolean, default=True)
#
#
# class Team(Base):
#     """Команды"""
#     __tablename__ = 'teams'
#
#     team_id = Column(Integer, primary_key=True)
#     name = Column(String(100), nullable=False, unique=True)
#
#     # Связи
#     participants = relationship("TournamentParticipant", back_populates="team")
#
#
# class TournamentParticipant(Base):
#     """Участники турнира"""
#     __tablename__ = 'tournament_participants'
#
#     participant_id = Column(Integer, primary_key=True)
#     full_name = Column(String(150), nullable=False)
#     short_name = Column(String(50), nullable=False)
#     gender = Column(String(1), nullable=False)  # 'M' или 'F'
#     age = Column(Integer, nullable=False)
#
#     team_id = Column(Integer, ForeignKey('teams.team_id'))
#
#     # Связи
#     team = relationship("Team", back_populates="participants")
#     sports = relationship("Sport", secondary=participant_sport, backref="participants")
#
#
#     __table_args__ = (
#         CheckConstraint("gender IN ('M', 'F')", name='check_gender_values'),
#         CheckConstraint("age > 0", name='check_age_positive')
#     )
