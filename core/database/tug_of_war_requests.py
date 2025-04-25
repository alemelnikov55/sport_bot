from typing import Dict, List, Tuple, Any

from sqlalchemy import select, update, or_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models import TugStatus, TugOfWarMatch


async def create_tug_matches(
        session: AsyncSession,
        groups_matches: Dict[str, List[Tuple[int, int]]]
) -> None:
    """
    Создает волейбольные матчи и сеты с учетом новой структуры таблицы VolleyballSet

    :param session: Асинхронная сессия для работы с БД
    :param groups_matches: Словарь вида {'Группа': [(id_команды1, id_команды2), ...]}
    """
    try:
        for group_name, matches in groups_matches.items():
            for team1_id, team2_id in matches:
                # Создаем новый матч
                new_match = TugOfWarMatch(
                    team1_id=team1_id,
                    team2_id=team2_id,
                    group_name=group_name,
                    status=TugStatus.NOT_STARTED,
                )

                session.add(new_match)
                await session.flush()  # Получаем match_id

        await session.commit()
        print(f"Создано {sum(len(m) for m in groups_matches.values())} матчей")
    except Exception as e:
        await session.rollback()
        print(f"Ошибка при создании матчей: {e}")
        raise


async def get_tug_matches(session: AsyncSession) -> List[Dict[str, Any]]:
    """
    Возвращает список матчей по перетягиванию каната с основной информацией.

    Формат возвращаемых данных:
    [
        {
            'match_id': int,
            'team1_name': str,
            'team2_name': str,
            'status': str
        },
        ...
    ]
    """
    # Получаем все матчи с предзагруженными командами
    result = await session.execute(
        select(TugOfWarMatch)
        .options(
            joinedload(TugOfWarMatch.team1),
            joinedload(TugOfWarMatch.team2)
        )
        .order_by(TugOfWarMatch.pull_id)
    )

    matches = result.unique().scalars().all()

    # Формируем список с основной информацией
    result = [
        {
            'pull_id': match.pull_id,
            'team1_name': match.team1.name,
            'team2_name': match.team2.name,
            'status': '♦️' if match.status == TugStatus.FINISHED else '🟢'
        }
        for match in matches
    ]

    return result


async def get_tug_match_info_by_id(session: AsyncSession, pull_id: int) -> Dict[str, Any]:
    """
    Возвращает информацию о матче по перетягиванию каната по его ID.

    Args:
        session: Асинхронная сессия SQLAlchemy
        pull_id: ID матча (pull_id в модели TugOfWarMatch)

    Returns:
        Словарь с информацией о матче:
        {
            'match_id': int,
            'team1_name': str,
            'team2_name': str,
            'team1_score': int,
            'team2_score': int,
            'is_started': bool,
            'is_in_process': bool,
            'status': str
        }
    """
    # Получаем матч с предзагруженными командами
    result = await session.execute(
        select(TugOfWarMatch)
        .options(
            joinedload(TugOfWarMatch.team1),
            joinedload(TugOfWarMatch.team2)
        )
        .where(TugOfWarMatch.pull_id == pull_id)
    )

    match = result.scalars().first()

    match_info = {
        'match_id': match.pull_id,
        'team1_name': match.team1.name,
        'team2_name': match.team2.name,
        'team1_score': match.score1,
        'team2_score': match.score2,
        'is_started': True if match.status is TugStatus.NOT_STARTED else False,
        'is_in_process': True if match.status is TugStatus.IN_PROGRESS else False
    }

    return match_info


async def get_tug_match_info_for_process_by_id(session: AsyncSession, pull_id: int) -> Dict[str, Any]:
    """
    Возвращает информацию о матче по перетягиванию каната по его ID.

    используется для вывода информации в окне get_tug_process_window
    :param session:
    :param pull_id:
    :return:
    """

    result = await session.execute(
        select(TugOfWarMatch)
        .options(
            joinedload(TugOfWarMatch.team1),
            joinedload(TugOfWarMatch.team2)
        )
        .where(TugOfWarMatch.pull_id == pull_id)
    )

    match = result.scalars().first()

    match_info = {
        'match_id': match.pull_id,
        'team1_name': match.team1.name,
        'team2_name': match.team2.name,
        'team1_id': match.team1.team_id,
        'team2_id': match.team2.team_id,
        'team1_score': match.score1,
        'team2_score': match.score2,
    }

    return match_info


async def update_tug_match_status(session: AsyncSession, pull_id: int,
                                  status: TugStatus = TugStatus.IN_PROGRESS) -> None:
    """
    Обновляет статус матча по перетягиванию каната.

    Args:
        session: Асинхронная сессия SQLAlchemy
        pull_id: ID матча (pull_id в модели TugOfWarMatch)
        status: Новый статус матча
    """

    stmt = (update(TugOfWarMatch)
            .where(TugOfWarMatch.pull_id == pull_id)
            .values(status=status))

    await session.execute(stmt)

    await session.commit()


async def increment_tug_match_score(session: AsyncSession, pull_id: int, scoring_team_id: int) -> None:
    """
    Увеличивает счет команды в матче по перетягиванию каната.

    Args:
        session: Асинхронная сессия SQLAlchemy
        pull_id: ID матча (pull_id в модели TugOfWarMatch)
        scoring_team_id: ID команды, чей счет нужно увеличить"""

    stmt = (update(TugOfWarMatch)
            .where(TugOfWarMatch.pull_id == pull_id)
            .where(or_(TugOfWarMatch.team1_id == scoring_team_id,
                       TugOfWarMatch.team2_id == scoring_team_id
                       )
                   )
            .values(
                score1=case(
                    (TugOfWarMatch.team1_id == scoring_team_id, TugOfWarMatch.score1 + 1),
                    else_=TugOfWarMatch.score1),
                score2=case(
                    (TugOfWarMatch.team2_id == scoring_team_id, TugOfWarMatch.score2 + 1),
                    else_=TugOfWarMatch.score2)
            )
            )

    await session.execute(stmt)
    await session.commit()


async def get_all_tug_matches_grouped(
        session: AsyncSession
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Возвращает матчи по перетягиванию каната, сгруппированные по группам.

    Returns:
        Словарь в формате:
        {
            'group_name1': [
                {
                    'team1': {
                        'name': str,
                        'score': int
                    },
                    'team2': {
                        'name': str,
                        'score': int
                    }
                },
                ...
            ],
            'group_name2': [...],
            ...
        }
    """
    # Получаем все матчи с предзагруженными командами
    result = await session.execute(
        select(TugOfWarMatch)
        .options(
            joinedload(TugOfWarMatch.team1),
            joinedload(TugOfWarMatch.team2)
        )
        .order_by(TugOfWarMatch.group_name, TugOfWarMatch.pull_id)
    )

    matches = result.unique().scalars().all()

    # Группируем матчи по названию группы
    grouped_matches = {}

    for match in matches:
        match_data = {
            'team1': {
                'name': match.team1.name,
                'score': match.score1
            },
            'team2': {
                'name': match.team2.name,
                'score': match.score2
            }
        }

        group_name = match.group_name or "Без группы"
        if group_name not in grouped_matches:
            grouped_matches[group_name] = []

        grouped_matches[group_name].append(match_data)

    return grouped_matches
