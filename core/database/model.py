# from sqlalchemy.orm import relationship
#
# from models_main import Base, TournamentParticipant
#
# # Добавляем связь обратно в TournamentParticipant после определения всех классов
# TournamentParticipant.football_goals = relationship(
#     "FootballGoal",
#     backref="participant"
# )