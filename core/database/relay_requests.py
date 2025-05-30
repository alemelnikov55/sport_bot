from datetime import datetime
from typing import List, Tuple, Dict, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Judges, Team
from database.models.relay_race_model import RelayResult


async def save_relay_result(session: AsyncSession,
                            team_id: int,
                            result_time: float,
                            judge_telegram_id: int) -> None:
    """
    Сохраняет результат забега участника в таблицу running_results.

    :param session: Асинхронная сессия SQLAlchemy
    :param team_id: ID команды
    :param result_time: Время в секундах (float)
    :param judge_telegram_id: ID судьи
    """

    judge_result = await session.execute(
        select(Judges.judge_id).where(Judges.telegram_id == judge_telegram_id)
    )

    judge_id = judge_result.scalar_one_or_none()

    new_result = RelayResult(
        team_id=team_id,
        result_time=round(result_time, 2),
        timestamp=datetime.now(),
        judge_id=judge_id,
    )

    session.add(new_result)
    await session.commit()


async def get_last_judge_reley_results(session: AsyncSession, telegram_id: int) -> Sequence[Tuple[str, int, float]]:
    """
    Возвращает последние 10 результатов, зарегистрированных судьей по telegram_id
    и указанной дистанции, в виде кортежей:
    (short_name, participant_id, result_time)

    :param session: Асинхронная сессия SQLAlchemy
    :param telegram_id: Telegram ID судьи
    :return: Список кортежей
    """
    # Получение judge_id
    result = await session.execute(
        select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    )

    judge_id = result.scalar_one_or_none()

    # Получение последних 10 результатов с join на участника
    query = (
        select(Team.name, RelayResult.result_time)
        .join(RelayResult, RelayResult.team_id == Team.team_id)
        .where(
            RelayResult.judge_id == judge_id,
        )
        .order_by(RelayResult.timestamp.desc())
        .limit(10)
    )
    result = await session.execute(query)
    return result.all()


async def get_relay_results(session: AsyncSession) -> List[Dict]:
    """
    Возвращает результаты всех забегов, сгруппированные по дистанции.
    Формат:
    {
        100: [
            {
                "team_name": "ОК Центр",
                "result_time": 12.45
            },
            ...
        ],
        ...
    }
    """
    stmt = (
        select(
            Team.name,
            RelayResult.result_time
        )
        .join(Team, Team.team_id == RelayResult.team_id)
    )

    result = await session.execute(stmt)
    rows = result.all()

    result = list()
    for team_name, result_time in rows:
        result.append({
            "team_name": team_name,
            "result_time": float(result_time)
        })

    return result
