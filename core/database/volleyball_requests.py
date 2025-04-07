"""
Модуль запросов для работы с волейбольными матчами
"""
from sqlalchemy import update, select, case, or_
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import Dict, List, Tuple, Optional
import datetime
from enum import Enum

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


async def update_match_status(
        session: AsyncSession,
        match_id: int,
        new_status: VolleyballMatchStatus,
        winner_id: Optional[int] = None
) -> None:
    """
    Обновляет статус волейбольного матча

    :param session: Асинхронная сессия SQLAlchemy
    :param match_id: ID матча
    :param new_status: Новый статус из VolleyballMatchStatus
    :param winner_id: ID команды-победителя (только для FINISHED)
    """
    await session.execute(
        update(VolleyballMatch)
        .where(VolleyballMatch.match_id == match_id)
        .values(
            status=new_status,
            winner_id=winner_id if new_status == VolleyballMatchStatus.FINISHED else None
        )
    )
    await session.commit()


async def update_set_status(
        session: AsyncSession,
        set_id: int,
        new_status: VolleyballMatchStatus
) -> None:
    """
    Обновляет статус сета в волейбольном матче

    :param session: Асинхронная сессия SQLAlchemy
    :param set_id: ID сета
    :param new_status: Новый статус из VolleyballMatchStatus
    """
    if new_status == VolleyballMatchStatus.FINISHED:
        # Получаем данные сета для определения победителя
        result = await session.execute(
            select(VolleyballSet)
            .where(VolleyballSet.set_id == set_id)
        )
        volleyball_set = result.scalar_one()

        # Обновляем счет в матче
        if volleyball_set.team1_score > volleyball_set.team2_score:
            await session.execute(
                update(VolleyballMatch)
                .where(VolleyballMatch.match_id == volleyball_set.match_id)
                .values(team1_set_wins=VolleyballMatch.team1_set_wins + 1)
            )
        else:
            await session.execute(
                update(VolleyballMatch)
                .where(VolleyballMatch.match_id == volleyball_set.match_id)
                .values(team2_set_wins=VolleyballMatch.team2_set_wins + 1)
            )

    # Обновляем статус сета
    await session.execute(
        update(VolleyballSet)
        .where(VolleyballSet.set_id == set_id)
        .values(status=new_status)
    )
    await session.commit()


async def increment_set_score(
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
