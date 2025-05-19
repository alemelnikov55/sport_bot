import asyncio
from pprint import pprint

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from typing import Type, Callable, Any

from database.models import (
    ExternalSportMapping, Sport, ExternalTeamMapping, Team, VolleyballMatchStatus, VolleyballMatch, MatchStatus,
    FootballMatch, async_session, TugOfWarMatch
)

# Общий статус маппинг типизирован
StatusMapper = Callable[[Any], str]


def status_mapper(status):
    return {
        "NOT_STARTED": "upcoming",
        "IN_PROGRESS": "ongoing",
        "FINISHED": "ended"
    }.get(status.name if hasattr(status, "name") else str(status).upper(), "unknown")


async def build_generic_tournament_data(
        session: AsyncSession,
        match_model: Type[Any],  # FootballMatch, VolleyballMatch и т.п.
        sport_name: str,
        extract_status: StatusMapper,  # функция status_enum → external str
        get_match_info: Callable[[Any, dict], dict]  # матч + карта команд → dict
) -> dict:
    # 1. Получаем внешний ID дисциплины
    sport_id = await session.scalar(
        select(Sport.sport_id).where(Sport.name.ilike(sport_name))
    )
    if not sport_id:
        raise ValueError(f"❌ Вид спорта '{sport_name}' не найден")

    discipline_id = await session.scalar(
        select(ExternalSportMapping.external_id).where(ExternalSportMapping.sport_id == sport_id)
    )
    if not discipline_id:
        raise ValueError(f"❌ Нет external_id для '{sport_name}' в ExternalSportMapping")

    # 2. Карта team_id → external_id
    ext_team_result = await session.execute(select(ExternalTeamMapping))
    team_map = {row.team_id: row.external_id for row in ext_team_result.scalars()}

    # 3. Загружаем все матчи
    matches = await session.scalars(select(match_model))
    stages = defaultdict(list)

    for match in matches:
        if match.team1_id not in team_map or match.team2_id not in team_map:
            print(f"⚠️ Пропущен матч {match.match_id}: нет external_id для одной из команд")
            continue

        match_data = get_match_info(match, team_map)
        match_data["status"] = extract_status(match.status)

        stage_key = getattr(match, "group_name", None) or "Без группы"
        stages[stage_key].append(match_data)

    load = {
        "disciplineId": discipline_id,
        "tournament": [
            {"stage": stage, "competitions": comps}
            for stage, comps in stages.items()
        ]
    }

    return load


# ===========================================
# VOLLEYBALL
# ===========================================
def volleyball_match_info(match, team_map):
    return {
        "id": str(match.match_id),
        "participants": [
            {"divisionId": team_map[match.team1_id]},
            {"divisionId": team_map[match.team2_id]}
        ]
    }


async def build_volleyball_tournament_data(session: AsyncSession):
    return await build_generic_tournament_data(
        session=session,
        match_model=VolleyballMatch,
        sport_name="Волейбол",
        extract_status=status_mapper,
        get_match_info=volleyball_match_info
    )


# ===========================================
# FOOTBALL
# ===========================================
def football_match_info(match, team_map):
    return {
        "id": str(match.match_id),
        "participants": [
            {"divisionId": team_map[match.team1_id]},
            {"divisionId": team_map[match.team2_id]}
        ]
    }


async def build_football_tournament_data(session: AsyncSession):
    return await build_generic_tournament_data(
        session=session,
        match_model=FootballMatch,
        sport_name="Мини-Футбол",
        extract_status=status_mapper,
        get_match_info=football_match_info
    )


# ===========================================
# TUG OF WAR
# ===========================================
def tug_match_info(match, team_map):
    return {
        "id": str(match.pull_id),
        "participants": [
            {"divisionId": team_map[match.team1_id]},
            {"divisionId": team_map[match.team2_id]}
        ]
    }


async def build_tug_of_war_tournament_data(session: AsyncSession):
    return await build_generic_tournament_data(
        session=session,
        match_model=TugOfWarMatch,
        sport_name="перетягивание каната",
        extract_status=status_mapper,
        get_match_info=tug_match_info
    )


async def main_():
    async with async_session() as session:
        pprint(await build_volleyball_tournament_data(session=session))
        pprint(await build_football_tournament_data(session=session))
        pprint(await build_tug_of_war_tournament_data(session=session))


if __name__ == "__main__":
    asyncio.run(main_())
