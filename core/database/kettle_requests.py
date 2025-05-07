import logging
from collections import defaultdict
from typing import List, Tuple, Dict, Any

from sqlalchemy import select, case
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Participant, KettleResult, Judges, Team

logger = logging.getLogger(__name__)


async def save_kettle_results(session: AsyncSession, lifter_id: int, count: int, telegram_id: int, category: str = None) -> None:
    """
    Сохраняет результаты гиревого спорта для участника в базу данных.

    :param session:
    :param lifter_id:
    :param count:
    :param telegram_id:
    :param category:
    :return:
    """
    result = await session.execute(
        select(Participant.team_id).where(Participant.participant_id == lifter_id)
    )

    team_id = result.scalar_one_or_none()

    judge_result = await session.execute(
        select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    )

    judge_id = judge_result.scalar_one_or_none()

    new_result = KettleResult(
        lifter_id=lifter_id,
        team_id=team_id,
        lift_count=count,
        category=category,
        judge_id=judge_id,
    )

    session.add(new_result)
    await session.commit()


async def get_all_kettle_results(session: AsyncSession) -> Dict[str, Any]:
    """
    Получает все результаты гиревого спорта из базы данных.

    :param session:
    :return:
    """
    stmt = (
        select(
            KettleResult.category,
            Participant.participant_id,
            Participant.full_name,
            Team.name,
            KettleResult.lift_count,
        )
        .join(Participant, KettleResult.lifter_id == Participant.participant_id)
        .join(Team, Team.team_id == KettleResult.team_id)
        .order_by(KettleResult.lift_count)
    )

    result = await session.execute(stmt)
    rows = result.all()

    grouped: Dict[str, List[Dict]] = defaultdict(list)

    for category, lifter_id, full_name, team_name, lift_count in rows:
        category = category if category else 'Без категории'
        grouped[category].append(
            {
                'participant_id': lifter_id,
                'full_name': full_name,
                'team_name': team_name,
                'lift_count': lift_count
            }
        )

    return dict(grouped)


async def get_kettle_export_results(session: AsyncSession) -> list[dict]:
    """
    Получает результаты гиревого спорта из базы данных и сортирует их по полу, категории и количеству повторений.
    """
    gender_order = case(
        (Participant.gender == 'M', 0),
        else_=1
    )

    stmt = (
        select(
            Participant.full_name,
            Team.name.label("team_name"),
            KettleResult.lift_count,
            KettleResult.category,
            Participant.age,
            Participant.gender
        )
        .join(Participant, KettleResult.lifter_id == Participant.participant_id)
        .join(Team, KettleResult.team_id == Team.team_id)
        .order_by(
            gender_order,  # сначала мужчины
            KettleResult.category.asc().nullsfirst(),  # категория по возрастанию (если есть)
            KettleResult.lift_count.desc()  # по убыванию числа повторений
        )
    )

    result = await session.execute(stmt)

    return [
        {
            'full_name': row.full_name,
            'team_name': row.team_name,
            'lift_count': row.lift_count,
            'category': row.category,
            'age': row.age,
            'gender': row.gender
        }
        for row in result.fetchall()
    ]


async def get_judge_history(session: AsyncSession, telegram_id: int) -> list[dict]:
    """
    Функция для получения истории последних 10 результатов гиревого спорта для судьи.
    """
    judge_stmt = select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    result = await session.execute(judge_stmt)
    judge_id = result.scalar_one_or_none()

    # Основной запрос по KettleResult
    stmt = (
        select(
            Participant.short_name,
            KettleResult.category,
            KettleResult.lift_count
        )
        .join(Participant, KettleResult.lifter_id == Participant.participant_id)
        .where(KettleResult.judge_id == judge_id)
        .order_by(KettleResult.timestamp.desc())
        .limit(10)
    )

    result = await session.execute(stmt)

    history_result = [
        {
            "short_name": row.short_name,
            "category": row.category,
            "lift_count": row.lift_count
        }
        for row in result.fetchall()
    ]

    return history_result
