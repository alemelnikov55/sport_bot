import logging
from collections import defaultdict
from typing import List, Tuple, Dict, Any

from sqlalchemy import select
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
