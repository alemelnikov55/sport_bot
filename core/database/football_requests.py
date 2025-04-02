from typing import Dict, Union, List, Optional, Any

from sqlalchemy import select, exists, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, aliased

from database.models import FootballGoal, FootballMatch, Participant, async_session, ParticipantSport, Sport, Team
from database.models import MatchStatus


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


async def add_goal(match_id: int, participant_id: int, half: int = 1) -> FootballMatch:
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


# под удаление
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


async def get_active_matches() -> Dict[str, List[Dict]]:
    """
    Возвращает все матчи не в статусе FINISHED, сгруппированные по группам.

    Returns:
        Словарь в формате:
        {
            "группа_A": [
                {
                    "match_id": int,
                    "team1": str,
                    "team2": str
                },
                ...
            ],
            "группа_B": [...],
            ...
        }
    """
    result = {}

    async with async_session() as session:
        # Запрос с предзагрузкой данных команд
        stmt = (
            select(FootballMatch)
            .options(
                joinedload(FootballMatch.team1),
                joinedload(FootballMatch.team2)
            )
            .where(FootballMatch.status != MatchStatus.FINISHED)
            .order_by(FootballMatch.group_name)
        )

        matches = (await session.execute(stmt)).scalars().all()

        for match in matches:
            group = match.group_name or "Без группы"

            if group not in result:
                result[group] = []

            match_data = {
                "match_id": match.match_id,
                "team1": match.team1.name,
                "team2": match.team2.name
            }
            result[group].append(match_data)

    return result


# async def get_match_teams_info(
#         session: AsyncSession,
#         match_id: int
# ) -> Optional[Dict[str, str]]:
#     """
#     Получает информацию о командах и группе матча по ID.
#
#     Args:
#         session: Асинхронная сессия SQLAlchemy
#         match_id: ID искомого матча
#
#     Returns:
#         Словарь с информацией о матче или None, если матч не найден
#     """
#     # Создаем алиасы для таблицы Team
#     Team1 = aliased(Team)
#     Team2 = aliased(Team)
#
#     result = await session.execute(
#         select(
#             Team1.name.label("team1_name"),
#             Team2.name.label("team2_name"),
#             FootballMatch.group_name
#         )
#         .select_from(FootballMatch)
#         .join(Team1, FootballMatch.team1_id == Team1.team_id, isouter=True)
#         .join(Team2, FootballMatch.team2_id == Team2.team_id, isouter=True)
#         .where(FootballMatch.match_id == match_id)
#     )
#
#     match_info = result.first()
#
#     if not match_info:
#         return None
#
#     return {
#         "team1": match_info.team1_name,
#         "team2": match_info.team2_name,
#         "group": match_info.group_name or "Без группы"
#     }


async def get_match_teams_info(
    session: AsyncSession,
    match_id: int
) -> Optional[Dict[str, Any]]:
    """
    Получает информацию о командах (с ID) и группе матча по ID.

    Args:
        session: Асинхронная сессия SQLAlchemy
        match_id: ID искомого матча

    Returns:
        Словарь с информацией о матче в формате:
        {
            "team1": {
                "name": "Название команды",
                "id": team_id
            },
            "team2": {
                "name": "Название команды",
                "id": team_id
            },
            "group": "Название группы"
        }
        или None, если матч не найден
    """
    # Создаем алиасы для таблицы Team
    Team1 = aliased(Team)
    Team2 = aliased(Team)

    result = await session.execute(
        select(
            Team1.name.label("team1_name"),
            Team1.team_id.label("team1_id"),
            Team2.name.label("team2_name"),
            Team2.team_id.label("team2_id"),
            FootballMatch.group_name
        )
        .select_from(FootballMatch)
        .join(Team1, FootballMatch.team1_id == Team1.team_id, isouter=True)
        .join(Team2, FootballMatch.team2_id == Team2.team_id, isouter=True)
        .where(FootballMatch.match_id == match_id)
    )

    match_info = result.first()

    if not match_info:
        return None

    return {
        "team1": {
            "name": match_info.team1_name,
            "id": match_info.team1_id
        },
        "team2": {
            "name": match_info.team2_name,
            "id": match_info.team2_id
        },
        "group": match_info.group_name or "Без группы"
    }


async def change_match_status(
        match_id: int,
        status: MatchStatus,
        session: AsyncSession
) -> Optional[Dict[str, str]]:
    """
    Изменяет статус матча и возвращает информацию о командах.

    Args:
        match_id: ID матча
        status: Новый статус матча
        session: Асинхронная сессия SQLAlchemy

    Returns:
        Словарь с названиями команд или None, если матч не найден
        {
            "team1": "Название команды 1",
            "team2": "Название команды 2"
        }
    """
    # 1. Сначала обновляем статус матча
    update_stmt = (
        update(FootballMatch)
        .where(FootballMatch.match_id == match_id)
        .values(status=status)
    )
    await session.execute(update_stmt)
    await session.commit()

    # 2. Затем получаем информацию о командах
    Team1 = aliased(Team)
    Team2 = aliased(Team)

    select_stmt = (
        select(
            Team1.name.label("team1_name"),
            Team2.name.label("team2_name")
        )
        .select_from(FootballMatch)
        .join(Team1, FootballMatch.team1_id == Team1.team_id)
        .join(Team2, FootballMatch.team2_id == Team2.team_id)
        .where(FootballMatch.match_id == match_id)
    )

    result = await session.execute(select_stmt)
    match_info = result.first()

    if not match_info:
        return None

    return {
        "team1": match_info.team1_name,
        "team2": match_info.team2_name
    }