# from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, CheckConstraint
# from sqlalchemy.orm import relationship
#
# from database.models_main import Base
#
#
# # class FootballMatch(Base):
# #     __tablename__ = 'football_matches'
# #
# #     match_id = Column(Integer, primary_key=True)
# #     team1_id = Column(Integer, ForeignKey('football_teams.team_id'), nullable=False)
# #     team2_id = Column(Integer, ForeignKey('football_teams.team_id'), nullable=False)
# #     group_name = Column(String(4), nullable=True)
# #     score1 = Column(Integer, default=0)
# #     score2 = Column(Integer, default=0)
# #     is_finished = Column(Boolean, default=False)
# #
# #     team1 = relationship("FootballTeam", foreign_keys=[team1_id])
# #     team2 = relationship("FootballTeam", foreign_keys=[team2_id])
# #
# #     __table_args__ = (
# #         CheckConstraint('team1_id != team2_id', name='check_different_teams'),
# #     )
# #
# #
# # class FootballGoal(Base):
# #     __tablename__ = 'football_goals'
# #
# #     goal_id = Column(Integer, primary_key=True)
# #     match_id = Column(Integer, ForeignKey('football_matches.match_id'), nullable=False)
# #     participant_id = Column(Integer, ForeignKey('tournament_participants.participant_id'), nullable=False)
# #     half = Column(Integer, nullable=False)
# #
# #     match = relationship("FootballMatch", backref="goals")
# #     participant = relationship("TournamentParticipant", back_populates="goals")
# #
# #     __table_args__ = (
# #         CheckConstraint('half IN (1, 2)', name='check_half_values'),
# #     )
#
# class FootballMatch(Base):
#     """Футбольные матчи"""
#     __tablename__ = 'football_matches'
#
#     match_id = Column(Integer, primary_key=True)
#     team1_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
#     team2_id = Column(Integer, ForeignKey('teams.team_id'), nullable=False)
#     group_name = Column(String(4))  # Группа (до 4 символов)
#     score1 = Column(Integer, default=0)
#     score2 = Column(Integer, default=0)
#     is_finished = Column(Boolean, default=False)
#
#     # Связи
#     team1 = relationship("Team", foreign_keys=[team1_id])
#     team2 = relationship("Team", foreign_keys=[team2_id])
#
#     __table_args__ = (
#         CheckConstraint('team1_id != team2_id', name='check_different_teams'),
#     )
#
#
# class FootballGoal(Base):
#     """Голы в футбольных матчах"""
#     __tablename__ = 'football_goals'
#
#     goal_id = Column(Integer, primary_key=True)
#     match_id = Column(Integer, ForeignKey('football_matches.match_id'), nullable=False)
#     participant_id = Column(Integer, ForeignKey('tournament_participants.participant_id'), nullable=False)
#     half = Column(Integer, nullable=False)  # 1 - первый тайм, 2 - второй тайм
#
#     # Связи
#     match = relationship("FootballMatch", backref="goals")
#     participant = relationship("TournamentParticipant", backref="football_goals")
#
#     __table_args__ = (
#         CheckConstraint('half IN (1, 2)', name='check_half_values'),
#     )