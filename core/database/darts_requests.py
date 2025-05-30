import logging
from typing import Dict, List

from sqlalchemy import update, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

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
        .limit(30)
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

    top_qualifiers = [
        {
            "player_id": row.participant_id,
            "name": row.short_name,
            "team_id": row.team_id,
            "team_name": row.team_name,
            "scores": row.score
        }
        for row in rows
    ]

    return top_qualifiers


async def get_darts_qualifiers_sorted(session: AsyncSession) -> list[dict]:
    stmt = (
        select(
            Participant.short_name,
            DartsQualifiers.score,
            Team.name.label("team_name")
        )
        .join(Participant, DartsQualifiers.player_id == Participant.participant_id)
        .join(Team, DartsQualifiers.team_id == Team.team_id)
        .order_by(DartsQualifiers.score.asc())
    )

    result = await session.execute(stmt)
    rows = result.fetchall()

    all_result = [
        {
            "short_name": row.short_name,
            "score": row.score,
            "team_name": row.team_name
        }
        for row in rows
    ]

    return all_result


async def create_darts_playoff_match(session: AsyncSession,
                                     player1_id: int,
                                     player2_id: int,
                                     playoff_type: DartsPlayoffType) -> DartsPlayOff:
    new_playoff = DartsPlayOff(
        player1_id=player1_id,
        player2_id=player2_id,
        playoff_type=playoff_type
    )

    session.add(new_playoff)
    await session.commit()
    await session.refresh(new_playoff)

    return new_playoff


async def get_playoff_match_info(session: AsyncSession, playoff_id: int) -> dict:
    # 1. Получаем сам плей-офф
    playoff_stmt = (
        select(
            DartsPlayOff.player1_id,
            DartsPlayOff.player2_id,
            DartsPlayOff.player1_wins,
            DartsPlayOff.player2_wins
        )
        .where(DartsPlayOff.playoff_id == playoff_id)
    )

    result = await session.execute(playoff_stmt)
    playoff = result.first()

    player1_id = playoff.player1_id
    player2_id = playoff.player2_id

    # 2. Получаем имена игроков
    players_stmt = (
        select(Participant.participant_id, Participant.short_name)
        .where(Participant.participant_id.in_([player1_id, player2_id]))
    )

    result = await session.execute(players_stmt)
    players = {row.participant_id: row.short_name for row in result.fetchall()}

    return {
        'player_1': {
            'id': player1_id,
            'name': players.get(player1_id),
            'scores': playoff.player1_wins
        },
        'player_2': {
            'id': player2_id,
            'name': players.get(player2_id),
            'scores': playoff.player2_wins
        }
    }


async def increment_player_win(session: AsyncSession, playoff_id: int, player_id: int) -> None:
    # Получаем запись плей-офф
    stmt = select(
        DartsPlayOff.playoff_id,
        DartsPlayOff.player1_id,
        DartsPlayOff.player2_id,
        DartsPlayOff.player1_wins,
        DartsPlayOff.player2_wins
    ).where(DartsPlayOff.playoff_id == playoff_id)

    result = await session.execute(stmt)
    playoff = result.first()

    if player_id == playoff.player1_id:
        new_wins = playoff.player1_wins + 1
        update_stmt = (
            update(DartsPlayOff)
            .where(DartsPlayOff.playoff_id == playoff_id)
            .values(player1_wins=new_wins)
        )
    elif player_id == playoff.player2_id:
        new_wins = playoff.player2_wins + 1
        update_stmt = (
            update(DartsPlayOff)
            .where(DartsPlayOff.playoff_id == playoff_id)
            .values(player2_wins=new_wins)
        )
    else:
        raise ValueError(f"Player with ID {player_id} is not part of playoff {playoff_id}")

    await session.execute(update_stmt)
    await session.commit()


async def update_playoff_winner(session: AsyncSession, playoff_id: int) -> None:
    # Получаем текущие данные по плей-офф
    stmt = select(
        DartsPlayOff.player1_id,
        DartsPlayOff.player2_id,
        DartsPlayOff.player1_wins,
        DartsPlayOff.player2_wins
    ).where(DartsPlayOff.playoff_id == playoff_id)

    result = await session.execute(stmt)
    playoff = result.first()

    if not playoff:
        raise ValueError(f"Playoff with ID {playoff_id} not found")

    # Логика определения победителя
    winner_id = None
    if playoff.player1_wins > playoff.player2_wins:
        winner_id = playoff.player1_id
    elif playoff.player2_wins > playoff.player1_wins:
        winner_id = playoff.player2_id
    # если равны — winner_id остаётся None

    if winner_id is not None:
        # Обновляем запись
        update_stmt = (
            update(DartsPlayOff)
            .where(DartsPlayOff.playoff_id == playoff_id)
            .values(winner_id=winner_id)
        )

        await session.execute(update_stmt)
        await session.commit()


async def get_all_playoffs_matches(session: AsyncSession) -> List[Dict]:
    # Создаём псевдонимы для трёх участников
    P1 = aliased(Participant)
    P2 = aliased(Participant)
    Winner = aliased(Participant)

    stmt = (
        select(
            DartsPlayOff.playoff_id,
            DartsPlayOff.player1_wins,
            DartsPlayOff.player2_wins,
            DartsPlayOff.playoff_type,
            P1.short_name.label("player1_name"),
            P2.short_name.label("player2_name"),
            Winner.short_name.label("winner_name")
        )
        .join(P1, DartsPlayOff.player1_id == P1.participant_id)
        .join(P2, DartsPlayOff.player2_id == P2.participant_id)
        .outerjoin(Winner, DartsPlayOff.winner_id == Winner.participant_id)
    )

    result = await session.execute(stmt)
    rows = result.fetchall()

    playoff_matches = [
        {
            "playoff_id": row.playoff_id,
            "player1_name": row.player1_name,
            "player2_name": row.player2_name,
            "player1_wins": row.player1_wins,
            "player2_wins": row.player2_wins,
            "playoff_type": row.playoff_type.value.split(' ')[0]  # enum → строка
        }
        for row in rows
    ]

    return playoff_matches


