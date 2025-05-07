import logging
from typing import Dict, List, Tuple, Optional, Any

from sqlalchemy import update, select, case, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DartsPlayoffType, DartsPlayOff, DartsQualifiers, Judges, Participant

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def add_darts_qualifiers_result(session: AsyncSession, player_id: int, team_id: int, score: int,
                                      telegram_id: int) -> None:
    """
    Добавляет участника в раунд квалификации.
    """
    judge_stmt = select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    result = await session.execute(judge_stmt)
    judge_id_row = result.scalar_one_or_none()

    new_qualifier = DartsQualifiers(
        player_id=player_id,
        team_id=team_id,
        score=score,
        judge_id=judge_id_row
    )
    session.add(new_qualifier)
    await session.commit()


async def get_darts_judge_history(session: AsyncSession, telegram_id: int) -> List[dict]:
    """
    Получает последние 10 записей сделанных судьей в квалификации дартса
    """
    judge_stmt = select(Judges.judge_id).where(Judges.telegram_id == telegram_id)
    result = await session.execute(judge_stmt)
    judge_id = result.scalar_one_or_none()

    stmt = (
        select(
            Participant.short_name,
            DartsQualifiers.score,
        )
        .join(Participant, DartsQualifiers.player_id == Participant.participant_id)
        .where(DartsQualifiers.judge_id == judge_id)
        .order_by(DartsQualifiers.timestamp.desc())
        .limit(10)
    )

    result = await session.execute(stmt)

    history_result = [
        {
            'short_name': row.short_name,
            'scores': row.score,
        }
        for row in result.fetchall()
    ]

    return history_result
