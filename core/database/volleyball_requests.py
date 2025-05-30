"""
Модуль запросов для работы с волейбольными матчами
"""
from typing import Dict, List, Tuple, Optional, Any

from sqlalchemy import update, select, case, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from database.models import Team
from database.models.volleybal_models import VolleyballSet, VolleyballMatch, VolleyballMatchStatus


async def create_volleyball_matches(
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
                new_match = VolleyballMatch(
                    team1_id=team1_id,
                    team2_id=team2_id,
                    group_name=group_name,
                    status=VolleyballMatchStatus.NOT_STARTED,
                    team1_set_wins=0,
                    team2_set_wins=0,
                )

                session.add(new_match)
                await session.flush()  # Получаем match_id

                # Создаем 3 сета (максимум для одного матча в волейболе)
                for set_num in range(1, 4):
                    new_set = VolleyballSet(
                        match_id=new_match.match_id,
                        team1_id=team1_id,  # Явная привязка к командам
                        team2_id=team2_id,
                        set_number=set_num,
                        status=VolleyballMatchStatus.NOT_STARTED,
                        team1_score=0,
                        team2_score=0
                    )
                    session.add(new_set)

        await session.commit()
        print(f"Создано {sum(len(m) for m in groups_matches.values())} матчей")
    except Exception as e:
        await session.rollback()
        print(f"Ошибка при создании матчей: {e}")
        raise


async def update_volleyball_match_status(
        session: AsyncSession,
        match_id: int,
        new_status: VolleyballMatchStatus,
        winner_id: Optional[int] = None
) -> None:
    """
    Обновляет статус волейбольного матча и автоматически определяет победителя
    на основе результатов сетов при завершении матча.

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча
    :param new_status: Новый статус из VolleyballMatchStatus
    :param winner_id: Опциональный ID победителя (если None, будет определен автоматически)
    :raises ValueError: Если статус FINISHED, но победитель не может быть определен
    """
    if new_status == VolleyballMatchStatus.FINISHED:
        # Получаем информацию о матче
        match_result = await session.execute(
            select(VolleyballMatch)
            .where(VolleyballMatch.match_id == match_id)
        )
        match = match_result.scalar_one()
        print(f"Проверка матча {match_id}: {match.team1_set_wins} - {match.team2_set_wins}")
        # Если победитель не указан явно, определяем его по сетам
        if winner_id is None:
            if match.team1_set_wins > match.team2_set_wins:
                winner_id = match.team1_id
            elif match.team2_set_wins > match.team1_set_wins:
                winner_id = match.team2_id
            else:
                raise ValueError("Невозможно определить победителя - равное количество выигранных сетов")

        # Обновляем только статус и победителя
        await session.execute(
            update(VolleyballMatch)
            .where(VolleyballMatch.match_id == match_id)
            .values(
                status=new_status,
                winner_id=winner_id
            )
        )
    else:
        # Для других статусов просто обновляем статус и сбрасываем победителя
        await session.execute(
            update(VolleyballMatch)
            .where(VolleyballMatch.match_id == match_id)
            .values(
                status=new_status,
                winner_id=None
            )
        )

    await session.commit()


async def update_volleyball_set_status(
        session: AsyncSession,
        match_id: int,
        set_number: int,
        new_status: VolleyballMatchStatus
) -> VolleyballSet | None:
    """
    Обновляет статус сета в волейбольном матче с проверкой соответствия set_id и match_id

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча (для проверки)
    :param set_number: номер сета
    :param new_status: Новый статус из VolleyballMatchStatus
    :raises ValueError: Если сет не принадлежит указанному матчу
    """
    # Получаем данные сета с проверкой принадлежности к матчу
    result = await session.execute(
        select(VolleyballSet)
        .where(
            VolleyballSet.set_number == set_number,
            VolleyballSet.match_id == match_id
        )
    )
    volleyball_set = result.scalar_one_or_none()
    # if volleyball_set is None:
    #     raise ValueError(f"Сет {set_number} не найден в матче {match_id}")

    if new_status == VolleyballMatchStatus.FINISHED:
        if volleyball_set.status == VolleyballMatchStatus.FINISHED:
            print("Сет уже завершен, пропускаем обновление")
            return None
        # Проверяем, что счет валидный
        if volleyball_set.team1_score == volleyball_set.team2_score:
            if volleyball_set.team1_score == 0:
                set_info = await session.execute(
                    update(VolleyballSet).returning(VolleyballSet)
                    .where(VolleyballSet.set_number == set_number)
                    .where(VolleyballSet.match_id == match_id)
                    .values(status=new_status)
                )
                await session.commit()
                return set_info.scalar_one_or_none()
            else:
                raise ValueError("Нельзя завершить сет с равным счетом")

        # Обновляем счет в матче
        if volleyball_set.team1_score > volleyball_set.team2_score:
            await session.execute(
                update(VolleyballMatch)
                .where(VolleyballMatch.match_id == match_id)
                .values(team1_set_wins=VolleyballMatch.team1_set_wins + 1)
            )
        else:
            await session.execute(
                update(VolleyballMatch)
                .where(VolleyballMatch.match_id == match_id)
                .values(team2_set_wins=VolleyballMatch.team2_set_wins + 1)
            )

    # Обновляем статус сета
    set_info = await session.execute(
        update(VolleyballSet).returning(VolleyballSet)
        .where(VolleyballSet.set_number == set_number)
        .where(VolleyballSet.match_id == match_id)
        .values(status=new_status)
    )
    await session.commit()
    return set_info.scalar_one_or_none()


async def increment_volleyball_set_score(
        session: AsyncSession,
        set_id: int,
        scoring_team_id: int
) -> None:
    """
    Быстрое увеличение счета без дополнительных проверок
    (использовать только если уверены в корректности данных)
    """
    # Одним запросом обновляем счет нужной команды
    await session.execute(
        update(VolleyballSet)
        .where(VolleyballSet.set_id == set_id)
        .where(or_(
            VolleyballSet.team1_id == scoring_team_id,
            VolleyballSet.team2_id == scoring_team_id
        ))
        .values(
            team1_score=case(
                (VolleyballSet.team1_id == scoring_team_id, VolleyballSet.team1_score + 1),
                else_=VolleyballSet.team1_score
            ),
            team2_score=case(
                (VolleyballSet.team2_id == scoring_team_id, VolleyballSet.team2_score + 1),
                else_=VolleyballSet.team2_score
            )
        )
    )
    await session.commit()
    return


async def get_volleyball_matches(session: AsyncSession) -> List[Dict[str, Any]]:
    """
        Возвращает все матчи, сгруппированные по группам.

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
    teams_scope = list()
    query = (select(VolleyballMatch)
             .options(joinedload(VolleyballMatch.team1),
                      joinedload(VolleyballMatch.team2)
                      )
             .order_by(VolleyballMatch.group_name))

    result = await session.execute(query)

    matches = result.scalars().all()

    for match in matches:
        match_data = {
            'group': match.group_name or 'NoGroup',
            "match_id": match.match_id,
            "team1": match.team1.name,
            "team2": match.team2.name,
            'status': '♦️' if match.status == VolleyballMatchStatus.FINISHED else '🟢'
        }
        teams_scope.append(match_data)

    return teams_scope


async def get_volleyball_matches_data(
        session: AsyncSession
) -> Dict[str, List[Dict]]:
    """
    Надежная версия с отдельными запросами для команд
    """
    # Получаем все матчи
    matches_result = await session.execute(
        select(VolleyballMatch)
        .options(
            joinedload(VolleyballMatch.team1),
            joinedload(VolleyballMatch.team2)
        )
        .order_by(VolleyballMatch.match_id)
    )
    matches = matches_result.scalars().all()

    grouped_matches = {}

    for match in matches:
        match_data = {
            'team_1': {
                'sets_won': match.team1_set_wins,
                'match_id': match.match_id,
                'name': match.team1.name
            },
            'team_2': {
                'sets_won': match.team2_set_wins,
                'match_id': match.match_id,
                'name': match.team2.name
            }
        }

        if match.group_name not in grouped_matches:
            grouped_matches[match.group_name] = []

        grouped_matches[match.group_name].append(match_data)
    print(grouped_matches)
    return grouped_matches


async def get_volleyball_match_info_by_id(session: AsyncSession, match_id: int) -> Dict[str, Any]:
    """
    Возвращает информацию о матче по его ID.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        match_id: ID матча.

    Returns:
    """
    stmt = select(VolleyballMatch).where(VolleyballMatch.match_id == match_id).options(
        selectinload(VolleyballMatch.team1),
        selectinload(VolleyballMatch.team2)
    )

    result = await session.execute(stmt)
    match = result.scalars().first()

    return {
        'match_id': match.match_id,
        'team1_name': match.team1.name,
        'team2_name': match.team2.name,
        'team1_score': match.team1_set_wins,
        'team2_score': match.team2_set_wins,
        'is_started': True if match.status is VolleyballMatchStatus.NOT_STARTED else False,
        'is_in_process': True if match.status is VolleyballMatchStatus.IN_PROGRESS else False,
        'is_finished': True if match.status is VolleyballMatchStatus.FINISHED else False
    }


async def get_current_volleyball_match_info(
        session: AsyncSession,
        match_id: int,
        set_number: int
) -> List[Dict]:
    """
    Возвращает информацию о волейбольном матче и указанном сете.

    :param session: AsyncSession
    :param match_id: ID матча
    :param set_number: номер сета
    :return: Список словарей с данными по каждой команде
    """
    # Получаем матч
    match_result = await session.execute(
        select(VolleyballMatch).where(VolleyballMatch.match_id == match_id)
    )
    match = match_result.scalar_one_or_none()
    if not match:
        return []

    # Получаем сет
    set_result = await session.execute(
        select(VolleyballSet).where(VolleyballSet.match_id == match_id)
        .where(VolleyballSet.set_number == set_number)
    )
    vset = set_result.scalar_one_or_none()
    if not vset:
        return []

    # Информация по командам
    info = []
    for team_id, set_wins, score in [
        (match.team1_id, match.team1_set_wins, vset.team1_score),
        (match.team2_id, match.team2_set_wins, vset.team2_score)
    ]:
        team_result = await session.execute(
            select(Team).where(Team.team_id == team_id)
        )
        team = team_result.scalar_one()
        info.append({
            "team_id": team.team_id,
            "team_name": team.name,
            "set_won": set_wins,
            "set_scores": score if score is not None else 0
        })

    return info

#Под удаление
# async def get_volleyball_set(session: AsyncSession, match_id: int, set_number: int) -> VolleyballSet:
#     """
#     Получает ID сета по ID матча и номеру сета.
#
#     :param session: AsyncSession
#     :param match_id: ID матча
#     :param set_number: номер сета
#     :return: ID сета или None, если сет не найден"""
#
#     stmt = (select(VolleyballSet)
#             .where(VolleyballSet.match_id == match_id).
#             where(VolleyballSet.set_number == set_number))
#
#     result = await session.execute(stmt)
#     set = result.scalar_one_or_none()
#
#     return set


async def get_volleyball_match_full_info(
        session: AsyncSession,
        match_id: int
) -> Dict[str, Any]:
    """
    Возвращает полную информацию о волейбольном матче в формате:

    {
        'match_id': int,
        'team1': {
            'id': int,
            'name': str,
            'sets_won': int
        },
        'team2': {
            'id': int,
            'name': str,
            'sets_won': int
        },
        'sets': [
            {
                'set_number': int,
                'team1_score': int,
                'team2_score': int,
                'status': str
            },
            ...
        ],
        'winner_id': Optional[int]
    }
    """
    # Получаем матч и отдельно загружаем связанные данные
    match_result = await session.execute(
        select(VolleyballMatch)
        .where(VolleyballMatch.match_id == match_id)
    )
    match = match_result.scalar_one_or_none()

    # Загружаем команды отдельно
    team1 = await session.get(Team, match.team1_id)
    team2 = await session.get(Team, match.team2_id)

    # Загружаем сеты для этого матча
    sets_result = await session.execute(
        select(VolleyballSet)
        .where(VolleyballSet.match_id == match_id)
        .order_by(VolleyballSet.set_number)
    )
    sets = sets_result.scalars().all()

    # Формируем результат
    result = {
        'match_id': match.match_id,
        'team1': {
            'id': match.team1_id,
            'name': team1.name,
            'sets_won': match.team1_set_wins
        },
        'team2': {
            'id': match.team2_id,
            'name': team2.name,
            'sets_won': match.team2_set_wins
        },
        'sets': [
            {
                'set_number': s.set_number,
                'team1_score': s.team1_score,
                'team2_score': s.team2_score,
                'status': s.status.value
            }
            for s in sets
        ],
        'winner_id': match.winner_id,
        'match_status': match.status.value
    }

    return result


async def get_next_available_set(
        session: AsyncSession,
        match_id: int
) -> VolleyballSet:
    """
    Возвращает номер сета с наименьшим значением, который имеет статус IN_PROGRESS или NOT_STARTED.
    Если таких сетов нет, возвращает None.

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча
    :return: Номер сета (1-3) или None, если нет доступных сетов
    """
    result = await session.execute(
        select(VolleyballSet)
        .where(
            VolleyballSet.match_id == match_id,
            VolleyballSet.status.in_([
                VolleyballMatchStatus.IN_PROGRESS,
                VolleyballMatchStatus.NOT_STARTED
            ])
        )
        .order_by(VolleyballSet.set_number)
        .limit(1)
    )

    set_number = result.scalar_one_or_none()
    return set_number


# под удаление
async def get_all_volleyball_matches(
        session: AsyncSession
) -> Dict[str, List[Dict]]:
    """
    Возвращает данные по всем волейбольным матчам с детализацией по сетам
    в формате:
    {
        'group_name': [
            {
                'team1': {
                    'name': str,
                    'sets_won': int,
                    'scores': [{'set_number': int, 'score': int}, ...]
                },
                'team2': {
                    'name': str,
                    'sets_won': int,
                    'scores': [{'set_number': int, 'score': int}, ...]
                }
            },
            ...
        ],
        ...
    }
    """
    # Получаем все активные матчи с предзагруженными командами и сетами
    result = await session.execute(
        select(VolleyballMatch)
        .options(
            joinedload(VolleyballMatch.team1),
            joinedload(VolleyballMatch.team2),
            joinedload(VolleyballMatch.sets)
        )
        .order_by(VolleyballMatch.group_name, VolleyballMatch.match_id)
    )

    matches = result.unique().scalars().all()

    # Группируем матчи по названию группы
    grouped_matches = {}

    for match in matches:
        # Сортируем сеты по номеру
        sorted_sets = sorted(match.sets, key=lambda x: x.set_number)

        # Формируем данные по командам
        team1_scores = []
        team2_scores = []

        for s in sorted_sets:
            team1_scores.append({
                'set_number': s.set_number,
                'score': s.team1_score
            })
            team2_scores.append({
                'set_number': s.set_number,
                'score': s.team2_score
            })

        match_data = {
            'team1': {
                'name': match.team1.name,
                'sets_won': match.team1_set_wins,
                'scores': team1_scores
            },
            'team2': {
                'name': match.team2.name,
                'sets_won': match.team2_set_wins,
                'scores': team2_scores
            }
        }

        if match.group_name not in grouped_matches:
            grouped_matches[match.group_name] = []

        grouped_matches[match.group_name].append(match_data)

    return grouped_matches
