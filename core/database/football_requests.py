from typing import Dict, List, Optional, Any

from sqlalchemy import select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, aliased, selectinload

from database.models import FootballGoal, FootballMatch, Participant, Team, \
    FootballFallers
from database.models import MatchStatus


async def create_match(session: AsyncSession, team1_id: int, team2_id: int, group_name: str = None) -> FootballMatch:
    async with session.begin():
        match = FootballMatch(
            team1_id=team1_id,
            team2_id=team2_id,
            group_name=group_name
        )
        session.add(match)
        await session.commit()
        return match


async def clear_matches(session: AsyncSession) -> str:
    async with session as session:
        stmt = delete(FootballGoal)
        await session.execute(stmt)
        stmt = delete(FootballMatch)
        await session.execute(stmt)
        await session.commit()
        return 'Таблица матчей удалена.'


async def add_goal(session: AsyncSession, match_id: int, participant_id: int, half: int = 1) -> FootballMatch:
    """Добавляет гол без проверки на участие в футболе"""
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

#
# # под удаление
# async def get_football_matches_with_goals(session: AsyncSession) -> Dict[str, Any]:
#     """
#     Возвращает статистику футбольных матчей с голами, сгруппированную по группам.
#     Учитывает связи через таблицы ParticipantSport и FootballGoal.
#     """
#     result = {"football": {}}
#
#     # Получаем ID футбола из таблицы Sport
#     football_sport = await session.execute(
#         select(Sport.sport_id).where(Sport.name == "football")
#     )
#     football_sport_id = football_sport.scalar_one_or_none()
#
#     if football_sport_id is None:
#         return result
#
#     # Получаем все матчи с предзагруженными командами и голами
#     matches_query = (
#         select(FootballMatch)
#         .options(
#             joinedload(FootballMatch.team1),
#             joinedload(FootballMatch.team2),
#             joinedload(FootballMatch.goals).joinedload(FootballGoal.scorer)
#         )
#     )
#     matches = (await session.execute(matches_query)).scalars().unique().all()
#
#     # Для каждого матча собираем данные
#     for match in matches:
#         group = match.group_name or "NoGroup"
#
#         if group not in result:
#             result[group] = []
#
#         # Получаем игроков, забивших голы в этом матче (уже предзагружены)
#         goal_scorers = [goal.scorer for goal in match.goals]
#
#         # Формируем данные по командам
#         team1_players = []
#         team2_players = []
#
#         for player in goal_scorers:
#
#             if player.team_id == match.team1_id:
#                 team1_players.append((player.short_name, player.participant_id))
#             else:
#                 team2_players.append((player.short_name, player.participant_id))
#
#         # Добавляем матч в результат
#         match_data = {
#             "team_1": {
#                 "match_id": match.match_id,
#                 "name": match.team1.name,
#                 "goals": match.score1,
#                 "players": team1_players
#             },
#             "team_2": {
#                 "match_id": match.match_id,
#                 "name": match.team2.name,
#                 "goals": match.score2,
#                 "players": team2_players
#             }
#         }
#
#         result[group].append(match_data)
#
#     return result


async def get_football_matches_with_goals_and_fallers(session: AsyncSession) -> dict:
    """
    Возвращает статистику футбольных матчей с голами и фолами, сгруппированную по группам.
    Формат возвращаемых данных:
    {
        "group_name": [
            {
                "team_1": {
                    "match_id": int,
                    "name": str,
                    "goals": int,
                    "players": [(short_name, participant_id)],  # забившие голы
                    "fallers": [(short_name, participant_id)]  # получившие фолы
                },
                "team_2": {
                    ...
                }
            },
            ...
        ],
        ...
    }
    """
    result = {}

    # Получаем все матчи с предзагруженными данными
    matches_query = (
        select(FootballMatch)
        .options(
            joinedload(FootballMatch.team1),
            joinedload(FootballMatch.team2),
            joinedload(FootballMatch.goals).joinedload(FootballGoal.scorer),
            joinedload(FootballMatch.fallers).joinedload(FootballFallers.faller)
        )
    )
    matches = (await session.execute(matches_query)).scalars().unique().all()

    for match in matches:
        group = match.group_name or "NoGroup"

        if group not in result:
            result[group] = []

        # Получаем игроков, забивших голы в этом матче
        goal_scorers = [goal.scorer for goal in match.goals if goal.scorer]

        # Получаем игроков, получивших фолы в этом матче
        fallers = [f.faller for f in match.fallers if f.faller]

        # Формируем данные по командам
        team1_data = {
            "match_id": match.match_id,
            "name": match.team1.name,
            "goals": match.score1,
            "players": []
        }

        team2_data = {
            "match_id": match.match_id,
            "name": match.team2.name,
            "goals": match.score2,
            "players": []
        }

        # Обрабатываем забивших голы
        for player in goal_scorers:

            if player.team_id == match.team1_id:
                team1_data["players"].append((player.short_name, player.participant_id))
            else:
                team2_data["players"].append((player.short_name, player.participant_id))

        formated_fallers = []

        # Обрабатываем получивших фолы
        for faller in fallers:

            formated_fallers.append((faller.short_name, faller.participant_id))

        # Добавляем матч в результат
        match_data = {
            'red_cards': formated_fallers,
            "team_1": team1_data,
            "team_2": team2_data
        }

        result[group].append(match_data)

    return result


async def get_active_matches(session: AsyncSession) -> List[Dict[str, Any]]:
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
    result = list()

    # Запрос с предзагрузкой данных команд
    stmt = (
        select(FootballMatch)
        .options(
            joinedload(FootballMatch.team1),
            joinedload(FootballMatch.team2)
        )
        .order_by(FootballMatch.group_name)
    )

    matches = (await session.execute(stmt)).scalars().all()

    for match in matches:
        match_data = {
            'group': match.group_name or "NoGroup",
            "match_id": match.match_id,
            "team1": match.team1.name,
            "team2": match.team2.name,
            'status': match.status
        }
        result.append(match_data)

    return result


async def get_match_teams_info(session: AsyncSession, match_id: int) -> Optional[Dict[str, Any]]:
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


async def get_match_info_by_id(session: AsyncSession, match_id: int) -> Dict[str, Any]:
    """
    Возвращает базовую информацию о матче: ID, названия команд и счет

    Args:
        match_id: ID матча
        session

    Returns:
        Словарь с минимальной информацией:
        {
            "match_id": int,
            "team1_name": str,
            "team2_name": str,
            "team1_score": int,
            "team2_score": int,
            "total_score": str  # в формате "X:Y"
        }
        или None, если матч не найден
    """
    stmt = select(FootballMatch).where(FootballMatch.match_id == match_id).options(
        selectinload(FootballMatch.team1),
        selectinload(FootballMatch.team2)
    )

    result = await session.execute(stmt)
    match = result.scalars().first()
    #
    # if not match:
    #     return None

    return {
        'match_id': match.match_id,
        'team1_name': match.team1.name,
        'team2_name': match.team2.name,
        'team1_score': match.score1,
        'team2_score': match.score2,
        'team1_id': match.team1_id,
        'team2_id': match.team2_id,
        'total_score': f'{match.score1}:{match.score2}'
    }


async def get_match_teams_optimized(session: AsyncSession, match_id: int) -> List[Dict[str, Any]]:
    """
    Оптимизированная версия с прямым JOIN запросом

    Возвращает список словарей с информацией о командах, участвующих в матче.

    returns: [{name: ..., id: ...}, {name: ..., id: ...}]
    """
    stmt = (
        select(
            Team.team_id.label("id"),
            Team.name
        )
        .select_from(FootballMatch)
        .join(Team, FootballMatch.team1_id == Team.team_id)
        .where(FootballMatch.match_id == match_id)
        .union_all(
            select(
                Team.team_id.label("id"),
                Team.name
            )
            .select_from(FootballMatch)
            .join(Team, FootballMatch.team2_id == Team.team_id)
            .where(FootballMatch.match_id == match_id)
        )
    )

    result = await session.execute(stmt)
    return [{"id": row.id, "name": row.name} for row in result.all()]


async def add_faller(session: AsyncSession, player_id: int, match_id: int) -> None:
    """Добавляет игрока как фаллера в матч."""
    faller = FootballFallers(faller_id=player_id, match_id=match_id)
    session.add(faller)
    await session.commit()


async def get_football_matches_for_team(session: AsyncSession, team_id: int) -> List[Dict[str, Any]]:
    """
    Возвращает все футбольные матчи для указанной команды

    :param session: Асинхронная сессия SQLAlchemy
    :param team_id: ID команды
    :return: Список словарей с информацией о матчах в формате:
        [
            {
                'match_id': int,
                'group_name': str,
                'status': str,
                'team1': {
                    'team_id': int,
                    'name': str,
                    'score': int
                },
                'team2': {
                    'team_id': int,
                    'name': str,
                    'score': int
                },
            },
            ...
        ]
    """
    # Основной запрос для матчей
    match_stmt = (
        select(FootballMatch)
        .where(or_(
            FootballMatch.team1_id == team_id,
            FootballMatch.team2_id == team_id
        ))
    )
    match_result = await session.execute(match_stmt)
    matches = match_result.scalars().all()

    if not matches:
        return []

    match_ids = [m.match_id for m in matches]

    # Получаем данные о командах
    team_ids = {m.team1_id for m in matches} | {m.team2_id for m in matches}
    team_stmt = select(Team).where(Team.team_id.in_(team_ids))
    team_result = await session.execute(team_stmt)
    teams = {t.team_id: t for t in team_result.scalars()}

    # Формируем итоговый результат
    result = [
        {
            'match_id': m.match_id,
            'group_name': m.group_name,
            'status': m.status.value,
            'team1': {
                'team_id': m.team1_id,
                'name': teams[m.team1_id].name,
                'score': m.score1
            },
            'team2': {
                'team_id': m.team2_id,
                'name': teams[m.team2_id].name,
                'score': m.score2
            },
        }
        for m in matches
    ]
    return result


async def get_team_goals_in_match(
        session: AsyncSession,
        match_id: int,
        team_id: int
) -> List[Dict[str, Any]]:
    """
    Возвращает все голы указанной команды в конкретном матче

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча
    :param team_id: ID команды
    :return: Список словарей с информацией о голах в формате:
        [
            {
                'goal_id': int,
                'scorer_id': int,
                'scorer_name': str,
                'half': int (1 или 2)
            },
            ...
        ]
    """
    # Проверяем, что команда участвует в матче
    match_stmt = select(FootballMatch).where(
        FootballMatch.match_id == match_id,
        or_(
            FootballMatch.team1_id == team_id,
            FootballMatch.team2_id == team_id
        )
    )
    match_result = await session.execute(match_stmt)
    if not match_result.scalar_one_or_none():
        return []

    # Получаем голы команды в матче
    stmt = (
        select(FootballGoal, Participant)
        .join(Participant, FootballGoal.scorer_id == Participant.participant_id, )
        .where(
            FootballGoal.match_id == match_id,
            Participant.team_id == team_id
        )
        .order_by(FootballGoal.id)
    )

    result = await session.execute(stmt)

    return [
        {
            'goal_id': goal.id,
            'scorer_id': scorer.participant_id,
            'scorer_name': scorer.short_name,
        }
        for goal, scorer in result
    ]


async def delete_goal(session: AsyncSession, match_id: int, goal_id: int, team_id: int) -> None:
    """Удаляет гол из таблицы FootballGoal."""
    stmt = delete(FootballGoal).where(FootballGoal.id == goal_id)
    await session.execute(stmt)

    match = await session.get(FootballMatch, match_id)

    if match.team1_id == team_id:
        match.score1 -= 1
    else:
        match.score2 -= 1

    await session.commit()

