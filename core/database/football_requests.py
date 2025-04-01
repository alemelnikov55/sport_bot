from typing import Dict, Union

from sqlalchemy import select, exists
from sqlalchemy.orm import joinedload

from database.models import FootballGoal, FootballMatch, Participant, async_session, ParticipantSport, Sport, Team


async def create_match(team1_id: int, team2_id: int, group_name: str = None) -> FootballMatch:
    async with async_session() as session:
        async with session.begin():
            match = FootballMatch(
                team1_id=team1_id,
                team2_id=team2_id,
                group_name=group_name
            )
            session.add(match)
            await session.commit()
            return match


async def add_goal(match_id: int, participant_id: int, half: int) -> FootballMatch:
    """Добавляет гол без проверки на участие в футболе"""
    async with async_session() as session:
        async with session.begin():
            goal = FootballGoal(
                match_id=match_id,
                scorer_id=participant_id,
                half=half
            )
            session.add(goal)

            match = await session.get(FootballMatch, match_id)
            participant = await session.get(Participant, participant_id)

            if match.team1_id == participant.team_id:
                match.score1 += 1
            else:
                match.score2 += 1

            await session.commit()
            return match


async def get_team_sport_participants(team_id: int, sport: Union[str, int]) -> Dict[str, int]:
    """
    Возвращает участников команды, которые играют в указанный вид спорта.

    Args:
        team_id: ID команды в таблице Team
        sport: вид спорта (название или sport_id)

    Returns:
        Словарь в формате {short_name: participant_id}
    """
    async with async_session() as session:
        # Определяем sport_id в зависимости от типа входного параметра
        if isinstance(sport, int):
            # Если передан ID вида спорта, проверяем его существование
            sport_exists = await session.execute(
                select(exists().where(Sport.sport_id == sport))
            )
            if not sport_exists.scalar():
                return {}
            sport_id = sport
        else:
            # Если передано название, ищем соответствующий ID
            sport_result = await session.execute(
                select(Sport.sport_id).where(Sport.name == sport.lower())
            )
            sport_id = sport_result.scalar_one_or_none()
            if sport_id is None:
                return {}

        # Выполняем основной запрос
        result = await session.execute(
            select(
                Participant.short_name,
                Participant.participant_id
            )
            .join(Participant.sports)  # Соединяем с таблицей participant_sports
            .where(
                Participant.team_id == team_id,
                ParticipantSport.sport_id == sport_id
            )
        )

        return {row.short_name: row.participant_id for row in result.all()}


async def get_football_matches_with_goals() -> dict:
    """
    Возвращает статистику футбольных матчей с голами, сгруппированную по группам.
    Учитывает связи через таблицы ParticipantSport и FootballGoal.
    """
    result = {"football": {}}

    async with async_session() as session:
        # Получаем ID футбола из таблицы Sport
        football_sport = await session.execute(
            select(Sport.sport_id).where(Sport.name == "football")
        )
        football_sport_id = football_sport.scalar_one_or_none()

        if football_sport_id is None:
            return result

        # Получаем все матчи с предзагруженными командами и голами
        matches_query = (
            select(FootballMatch)
            .options(
                joinedload(FootballMatch.team1),
                joinedload(FootballMatch.team2),
                joinedload(FootballMatch.goals).joinedload(FootballGoal.scorer)
            )
        )
        matches = (await session.execute(matches_query)).scalars().unique().all()

        # Для каждого матча собираем данные
        for match in matches:
            group = match.group_name or "NoGroup"

            if group not in result["football"]:
                result["football"][group] = []

            # Получаем игроков, забивших голы в этом матче (уже предзагружены)
            goal_scorers = [goal.scorer for goal in match.goals]

            # Формируем данные по командам
            team1_players = []
            team2_players = []

            for player in goal_scorers:
                # Проверяем, что игрок действительно играет в футбол
                plays_football = await session.execute(
                    select(exists().where(
                        ParticipantSport.participant_id == player.participant_id,
                        ParticipantSport.sport_id == football_sport_id
                    ))
                )

                if not plays_football.scalar():
                    continue

                if player.team_id == match.team1_id:
                    team1_players.append((player.short_name, player.participant_id))
                else:
                    team2_players.append((player.short_name, player.participant_id))

            # Добавляем матч в результат
            match_data = {
                "team_1": {
                    "match_id": match.match_id,
                    "name": match.team1.name,
                    "goals": match.score1,
                    "players": team1_players
                },
                "team_2": {
                    "match_id": match.match_id,
                    "name": match.team2.name,
                    "goals": match.score2,
                    "players": team2_players
                }
            }

            result["football"][group].append(match_data)

    return result