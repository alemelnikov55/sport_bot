import logging
from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database.models import Participant, RunningResult, Judges


async def save_running_result(session: AsyncSession,
                              participant_id: int,
                              result_time: float,
                              distance_m: int,
                              judge_telegram_id: int) -> None:
    """
    Сохраняет результат забега участника в таблицу running_results.

    :param session: Асинхронная сессия SQLAlchemy
    :param participant_id: ID участника
    :param result_time: Время в секундах (float)
    :param distance_m: Дистанция в метрах
    :param judge_telegram_id: ID судьи
    """
    result = await session.execute(
        select(Participant.team_id).where(Participant.participant_id == participant_id)
    )

    team_id = result.scalar_one_or_none()
    if team_id is None:
        raise ValueError(f"Участник с ID {participant_id} не найден")

    judge_result = await session.execute(
        select(Judges.judge_id).where(Judges.telegram_id == judge_telegram_id)
    )

    judge_id = judge_result.scalar_one_or_none()

    new_result = RunningResult(
        participant_id=participant_id,
        team_id=team_id,
        distance_m=distance_m,
        result_time=round(result_time, 2),
        timestamp=datetime.now(),
        judge_id=judge_id,
    )

    session.add(new_result)
    await session.commit()


async def get_last_judge_results(session: AsyncSession, telegram_id: int, distance_m: int) -> List[Tuple[str, int, float]]:
    """
    Возвращает последние 10 результатов, зарегистрированных судьей по telegram_id
    и указанной дистанции, в виде кортежей:
    (short_name, participant_id, result_time)

    :param session: Асинхронная сессия SQLAlchemy
    :param telegram_id: Telegram ID судьи
    :param distance_m: Дистанция (в метрах)
    :return: Список кортежей
    """
    # Получение judge_id
    result = await session.execute(
        select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    )
    judge_id = result.scalar_one_or_none()
    if judge_id is None:
        raise ValueError(f"Судья с telegram_id={telegram_id} не найден.")

    # Получение последних 10 результатов с join на участника
    query = (
        select(Participant.short_name, Participant.participant_id, RunningResult.result_time)
        .join(RunningResult, RunningResult.participant_id == Participant.participant_id)
        .where(
            RunningResult.judge_id == judge_id,
            RunningResult.distance_m == distance_m
        )
        .order_by(RunningResult.timestamp.desc())
        .limit(10)
    )
    result = await session.execute(query)
    return result.all()

