import logging
from collections import defaultdict
from typing import List, Tuple, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Participant, RunningResult, Judges, Team

logger = logging.getLogger(__name__)


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

    judge_result = await session.execute(
        select(Judges.judge_id).where(Judges.telegram_id == judge_telegram_id)
    )

    judge_id = judge_result.scalar_one_or_none()

    new_result = RunningResult(
        participant_id=participant_id,
        team_id=team_id,
        distance_m=distance_m,
        result_time=round(result_time, 2),
        judge_id=judge_id,
    )

    session.add(new_result)
    await session.commit()


async def get_last_judge_run_results(session: AsyncSession, telegram_id: int, distance_m: int) -> Sequence[Tuple[str, int, float]]:
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


async def get_running_results_by_distance(session: AsyncSession) -> Dict[str, List[Dict]]:
    """
    Возвращает результаты всех забегов, сгруппированные по дистанции.
    Формат:
    {
        100: [
            {
                "participant_id": 1,
                "full_name": "Иванов Иван",
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
            RunningResult.distance_m,
            Participant.participant_id,
            Participant.full_name,
            Team.name,
            RunningResult.result_time
        )
        .join(Participant, RunningResult.participant_id == Participant.participant_id)
        .join(Team, Team.team_id == RunningResult.team_id)
        .order_by(RunningResult.distance_m, RunningResult.result_time)
    )

    result = await session.execute(stmt)
    rows = result.all()

    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for distance, participant_id, full_name, team_name, result_time in rows:
        distance = str(distance)
        grouped[distance].append({
            "participant_id": participant_id,
            "full_name": full_name,
            "team_name": team_name,
            "result_time": float(result_time)
        })

    return dict(grouped)

