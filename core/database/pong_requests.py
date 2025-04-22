import logging
from typing import Dict, List, Tuple, Optional, Any

from sqlalchemy import update, select, case, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from database.models.pong_models import PongMatchStatus, TableTennisMatch, TableTennisSet

logger = logging.getLogger(__name__)


async def create_pong_matches(
        session: AsyncSession,
        groups_matches: Dict[str, List[Tuple[int, int]]]
) -> None:
    """
    Создает матчи и сеты по настольному теннису

    :param session: Асинхронная сессия для работы с БД
    :param groups_matches: Словарь вида {'Группа': [(id_команды1, id_команды2), ...]}
    """
    try:
        for group_name, matches in groups_matches.items():
            for player1_id, player2_id in matches:
                # Создаем новый матч
                new_match = TableTennisMatch(
                    player1_id=player1_id,
                    player2_id=player2_id,
                    group_name=group_name,
                    status=PongMatchStatus.NOT_STARTED,
                    player1_set_wins=0,
                    player2_set_wins=0,
                )

                session.add(new_match)
                await session.flush()  # Получаем match_id

                # Создаем 3 сета (максимум для одного матча в волейболе)
                for set_num in range(1, 4):
                    new_set = TableTennisSet(
                        match_id=new_match.match_id,
                        player1_id=player1_id,  # Явная привязка к командам
                        player2_id=player2_id,
                        set_number=set_num,
                        status=PongMatchStatus.NOT_STARTED,
                        player1_score=0,
                        player2_score=0
                    )
                    session.add(new_set)

        await session.commit()
        print(f"Создано {sum(len(m) for m in groups_matches.values())} матчей")
    except Exception as e:
        await session.rollback()
        print(f"Ошибка при создании матчей: {e}")
        raise


async def update_pong_match_status(
        session: AsyncSession,
        match_id: int,
        new_status: PongMatchStatus,
        winner_id: Optional[int] = None
) -> None:
    """
    Обновляет статус волейбольного матча и автоматически определяет победителя
    на основе результатов сетов при завершении матча.

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча
    :param new_status: Новый статус из TableTennisMatchStatus
    :param winner_id: Опциональный ID победителя (если None, будет определен автоматически)
    :raises ValueError: Если статус FINISHED, но победитель не может быть определен
    """
    if new_status == PongMatchStatus.FINISHED:
        # Получаем информацию о матче
        match_result = await session.execute(
            select(TableTennisMatch)
            .where(TableTennisMatch.match_id == match_id)
        )
        match = match_result.scalar_one()
        print(f"Проверка матча {match_id}: {match.player1_set_wins} - {match.player2_set_wins}")
        # Если победитель не указан явно, определяем его по сетам
        if winner_id is None:
            if match.player1_set_wins > match.player2_set_wins:
                winner_id = match.player1_id
            elif match.player2_set_wins > match.player1_set_wins:
                winner_id = match.player2_id
            else:
                raise ValueError("Невозможно определить победителя - равное количество выигранных сетов")

        # Обновляем только статус и победителя
        await session.execute(
            update(TableTennisMatch)
            .where(TableTennisMatch.match_id == match_id)
            .values(
                status=new_status,
                winner_id=winner_id
            )
        )
    else:
        # Для других статусов просто обновляем статус и сбрасываем победителя
        await session.execute(
            update(TableTennisMatch)
            .where(TableTennisMatch.match_id == match_id)
            .values(
                status=new_status,
                winner_id=None
            )
        )

    await session.commit()


async def update_pong_set_status(
        session: AsyncSession,
        match_id: int,
        set_number: int,
        new_status: PongMatchStatus
) -> TableTennisSet:
    """
    Обновляет статус сета в теннисном матче с проверкой соответствия set_id и match_id

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча (для проверки)
    :param set_number: номер сета
    :param new_status: Новый статус из VolleyballMatchStatus
    :raises ValueError: Если сет не принадлежит указанному матчу
    """
    # Получаем данные сета с проверкой принадлежности к матчу
    result = await session.execute(
        select(TableTennisSet)
        .where(
            TableTennisSet.set_number == set_number,
            TableTennisSet.match_id == match_id
        )
    )
    volleyball_set = result.scalar_one_or_none()
    if volleyball_set is None:
        raise ValueError(f"Сет {set_number} не найден в матче {match_id}")

    if new_status == PongMatchStatus.FINISHED:
        if volleyball_set.status == PongMatchStatus.FINISHED:
            print("Сет уже завершен, пропускаем обновление")
            return
        # Проверяем, что счет валидный
        if volleyball_set.player1_score == volleyball_set.player2_score:
            if volleyball_set.player1_score == 0:
                set_info = await session.execute(
                    update(TableTennisSet).returning(TableTennisSet)
                    .where(TableTennisSet.set_number == set_number)
                    .where(TableTennisSet.match_id == match_id)
                    .values(status=new_status)
                )
                await session.commit()
                return set_info.scalar_one_or_none()
            else:
                raise ValueError("Нельзя завершить сет с равным счетом")

        # Обновляем счет в матче
        if volleyball_set.player1_score > volleyball_set.player2_score:
            await session.execute(
                update(TableTennisMatch)
                .where(TableTennisMatch.match_id == match_id)
                .values(player1_set_wins=TableTennisMatch.player1_set_wins + 1)
            )
        else:
            await session.execute(
                update(TableTennisMatch)
                .where(TableTennisMatch.match_id == match_id)
                .values(player2_set_wins=TableTennisMatch.player2_set_wins + 1)
            )

    # Обновляем статус сета
    set_info = await session.execute(
        update(TableTennisSet).returning(TableTennisSet)
        .where(TableTennisSet.set_number == set_number)
        .where(TableTennisSet.match_id == match_id)
        .values(status=new_status)
    )
    await session.commit()
    return set_info.scalar_one_or_none()


async def increment_pong_set_score(
        session: AsyncSession,
        set_id: int,
        scoring_player_id: int
) -> None:
    """
    Увеличивает счет участника в сете по настольному теннису

    :param session: Асинхронная сессия SQLAlchemy
    :param set_id: ID сета
    :param scoring_player_id: ID участника, который заработал очко
    """
    await session.execute(
        update(TableTennisSet)
        .where(TableTennisSet.set_id == set_id)
        .where(or_(
            TableTennisSet.player1_id == scoring_player_id,
            TableTennisSet.player2_id == scoring_player_id
        ))
        .values(
            player1_score=case(
                (TableTennisSet.player1_id == scoring_player_id,
                 TableTennisSet.player1_score + 1),
                else_=TableTennisSet.player1_score
            ),
            player2_score=case(
                (TableTennisSet.player2_id == scoring_player_id,
                 TableTennisSet.player2_score + 1),
                else_=TableTennisSet.player2_score
            )
        )
    )
    await session.commit()


async def get_pong_matches(session: AsyncSession) -> List[Dict[str, Any]]:
    """
    Возвращает все матчи по настольному теннису, сгруппированные по группам.

    Returns:
        Список словарей в формате:
        [
            {
                "match_id": int,
                "player1": {
                    "id": int,
                    "name": str
                },
                "player2": {
                    "id": int,
                    "name": str
                },
            },
            ...
        ]
    """
    query = (
        select(TableTennisMatch)
        .options(
            joinedload(TableTennisMatch.player1),
            joinedload(TableTennisMatch.player2)
        )
        .order_by(TableTennisMatch.group_name, TableTennisMatch.match_id)
    )

    result = await session.execute(query)
    matches = result.unique().scalars().all()
    matches_data = []
    for match in matches:
        match_info = {
            "match_id": match.match_id,
            "player1": f'{match.player1.short_name} {match.player1_id}',
            "player2": f'{match.player2.short_name} {match.player2_id}',
            'status': '♦️' if match.status == PongMatchStatus.FINISHED else '🟢'
        }
        matches_data.append(match_info)

    return matches_data


async def get_pong_match_info_by_id(
        session: AsyncSession,
        match_id: int
) -> Dict[str, Any]:
    """
    Возвращает информацию о матче по настольному теннису по его ID.

    Args:
        session: Асинхронная сессия SQLAlchemy.
        match_id: ID матча.

    Returns:
        Словарь с информацией о матче:
        {
            'match_id': int,
            'player1': {'id': int, 'name': str},
            'player2': {'id': int, 'name': str},
            'player1_score': int,
            'player2_score': int,
            'is_started': bool,
            'is_in_process': bool,
            'status': str
        }
    """
    stmt = (
        select(TableTennisMatch)
        .where(TableTennisMatch.match_id == match_id)
        .options(
            selectinload(TableTennisMatch.player1),
            selectinload(TableTennisMatch.player2)
        )
    )

    result = await session.execute(stmt)
    match = result.scalars().first()

    if not match:
        raise ValueError(f"Матч с ID {match_id} не найден")

    return {
        'match_id': match.match_id,
        'player1': f'{match.player1.short_name} {match.player1_id}',
        'player2': f'{match.player2.short_name} {match.player2_id}',
        'player1_score': match.player1_set_wins,
        'player2_score': match.player2_set_wins,
        'is_started': True if match.status is PongMatchStatus.NOT_STARTED else False,
        'is_in_process': True if match.status is PongMatchStatus.IN_PROGRESS else False,
    }


async def get_pong_next_available_set(
        session: AsyncSession,
        match_id: int
) -> TableTennisSet:
    """
    Возвращает номер сета с наименьшим значением, который имеет статус IN_PROGRESS или NOT_STARTED.
    Если таких сетов нет, возвращает None.

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча по настольному теннису
    :return: Номер сета (1-3) или None, если нет доступных сетов
    """
    logger.info("Получение следующего доступного сета для матча %s", match_id)
    result = await session.execute(
        select(TableTennisSet)
        .where(
            TableTennisSet.match_id == match_id,
            TableTennisSet.status.in_([
                PongMatchStatus.IN_PROGRESS,
                PongMatchStatus.NOT_STARTED
            ])
        )
        .order_by(TableTennisSet.set_number)
        .limit(1)
    )

    set_info = result.scalar_one_or_none()
    return set_info


async def get_current_table_tennis_match_info(
    session: AsyncSession,
    match_id: int,
    set_number: int
) -> List[Dict]:
    """
    Возвращает информацию о матче по настольному теннису и указанном сете.

    :param session: AsyncSession
    :param match_id: ID матча
    :param set_number: номер сета (1-3)
    :return: Список словарей с данными по каждому игроку:
        [
            {
                "player_id": int,
                "player_name": str,
                "sets_won": int,
                "current_set_score": int
            },
            ...
        ]
    """
    # Получаем матч с предзагруженными игроками
    match_result = await session.execute(
        select(TableTennisMatch)
        .options(
            joinedload(TableTennisMatch.player1),
            joinedload(TableTennisMatch.player2)
        )
        .where(TableTennisMatch.match_id == match_id)
    )
    match = match_result.scalar_one_or_none()
    if not match:
        return []

    # Получаем указанный сет
    set_result = await session.execute(
        select(TableTennisSet)
        .where(
            TableTennisSet.match_id == match_id,
            TableTennisSet.set_number == set_number
        )
    )
    tennis_set = set_result.scalar_one_or_none()
    if not tennis_set:
        return []

    # Формируем информацию по игрокам
    players_info = []
    for player, sets_won, score in [
        (match.player1, match.player1_set_wins, tennis_set.player1_score),
        (match.player2, match.player2_set_wins, tennis_set.player2_score)
    ]:
        players_info.append({
            "player_id": player.participant_id,
            "player_name": player.short_name,
            "sets_won": sets_won,
            "current_set_score": score if score is not None else 0
        })

    return players_info


async def get_pong_match_full_info(
        session: AsyncSession,
        match_id: int
) -> Dict[str, Any]:
    """
    Возвращает полную информацию о матче по настольному теннису в формате:

    {
        'match_id': int,
        'player1': {
            'id': int,
            'name': str,
            'sets_won': int
        },
        'player2': {
            'id': int,
            'name': str,
            'sets_won': int
        },
        'sets': [
            {
                'set_number': int,
                'player1_score': int,
                'player2_score': int,
                'status': str
            },
            ...
        ],
        'winner_id': Optional[int],
        'match_status': str
    }
    """
    # Получаем матч с предзагруженными игроками
    match_result = await session.execute(
        select(TableTennisMatch)
        .options(
            joinedload(TableTennisMatch.player1),
            joinedload(TableTennisMatch.player2),
            joinedload(TableTennisMatch.sets)
        )
        .where(TableTennisMatch.match_id == match_id)
    )
    match = match_result.unique().scalar_one_or_none()

    if not match:
        return {}

    # Сортируем сеты по номеру
    sorted_sets = sorted(match.sets, key=lambda x: x.set_number)

    # Формируем результат
    result = {
        'match_id': match.match_id,
        'player1': {
            'id': match.player1_id,
            'name': match.player1.short_name,
            'sets_won': match.player1_set_wins
        },
        'player2': {
            'id': match.player2_id,
            'name': match.player2.short_name,
            'sets_won': match.player2_set_wins
        },
        'sets': [
            {
                'set_number': s.set_number,
                'player1_score': s.player1_score,
                'player2_score': s.player2_score,
                'status': s.status.value
            }
            for s in sorted_sets
        ],
        'match_status': match.status.value
    }

    return result


async def get_all_pong_matches_grouped(
        session: AsyncSession
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Возвращает все матчи по настольному теннису, сгруппированные по группам.

    Формат возвращаемых данных:
    {
        "group_name1": [
            {
                'match_id': int,
                'player1': {
                    'id': int,
                    'name': str,
                    'sets_won': int
                },
                'player2': {
                    'id': int,
                    'name': str,
                    'sets_won': int
                },
                'sets': [
                    {
                        'set_number': int,
                        'player1_score': int,
                        'player2_score': int,
                        'status': str
                    },
                    ...
                ],
                'winner_id': Optional[int],
                'match_status': str
            },
            ...
        ],
        "group_name2": [...],
        ...
    }
    """
    # Получаем все матчи с предзагруженными данными
    matches_result = await session.execute(
        select(TableTennisMatch)
        .options(
            joinedload(TableTennisMatch.player1),
            joinedload(TableTennisMatch.player2),
            joinedload(TableTennisMatch.sets),
            joinedload(TableTennisMatch.winner)
        )
        .order_by(TableTennisMatch.group_name, TableTennisMatch.match_id)
    )

    matches = matches_result.unique().scalars().all()

    # Группируем матчи по названию группы
    grouped_matches = {}

    for match in matches:
        # Сортируем сеты по номеру
        sorted_sets = sorted(match.sets, key=lambda x: x.set_number)

        match_data = {
            'match_id': match.match_id,
            'player1': {
                'id': match.player1_id,
                'name': match.player1.short_name,
                'sets_won': match.player1_set_wins
            },
            'player2': {
                'id': match.player2_id,
                'name': match.player2.short_name,
                'sets_won': match.player2_set_wins
            },
            'sets': [
                {
                    'set_number': s.set_number,
                    'player1_score': s.player1_score,
                    'player2_score': s.player2_score,
                    'status': s.status.value
                }
                for s in sorted_sets
            ],
            'winner_id': match.winner_id,
            'match_status': match.status.value
        }

        # Добавляем в соответствующую группу
        group_name = match.group_name or "Без группы"
        if group_name not in grouped_matches:
            grouped_matches[group_name] = []

        grouped_matches[group_name].append(match_data)

    return grouped_matches