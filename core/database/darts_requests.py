import logging
from typing import Dict, List, Tuple, Optional, Any

from sqlalchemy import update, select, case, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DartsPlayoffType, DartsPlayOff, DartsQualifiers, Judges, Participant, Team

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


async def get_top_darts_qualifiers(session: AsyncSession) -> list[dict]:
    """
    Получает топ-10 участников квалификации дартса, которые имеют наибольшее количество очков.

    Может вернуть больше участников, если у замыкающих одинаковое число очков
    """
    # 1. Подзапрос: определить минимальное значение очков в топ-10
    subquery = (
        select(DartsQualifiers.score)
        .order_by(DartsQualifiers.score.desc())
        .limit(10)
    ).subquery()

    # Получаем минимальное значение в топ-10
    min_score_stmt = select(func.min(subquery.c.score))
    result = await session.execute(min_score_stmt)
    min_score = result.scalar_one()

    # 2. Основной запрос: выбрать всех игроков с очками >= min_score
    stmt = (
        select(
            Participant.participant_id,
            Participant.short_name,
            Team.team_id,
            Team.name.label("team_name"),
            DartsQualifiers.score
        )
        .join(Participant, DartsQualifiers.player_id == Participant.participant_id)
        .join(Team, DartsQualifiers.team_id == Team.team_id)
        .where(DartsQualifiers.score >= min_score)
        .order_by(DartsQualifiers.score.desc())
    )

    result = await session.execute(stmt)
    rows = result.fetchall()

    return [
        {
            "player_id": row.participant_id,
            "name": row.short_name,
            "team_id": row.team_id,
            "team_name": row.team_name,
            "scores": row.score
        }
        for row in rows
    ]


async def create_darts_playoff_match(session: AsyncSession,
                                     player1_id: int,
                                     player2_id: int,
                                     playoff_type: DartsPlayoffType) -> None:
    new_playoff = DartsPlayOff(
        player1_id=player1_id,
        player2_id=player2_id,
        playoff_type=playoff_type
    )

    session.add(new_playoff)
    await session.commit()
