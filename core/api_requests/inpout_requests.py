from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.main_models import Participant, Team, Sport, ParticipantSport
from database.models.mapping_models import ExternalTeamMapping, ExternalSportMapping
from sqlalchemy import select
from typing import List, Dict


def calculate_age(birthdate_str: str) -> int:
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))


def format_full_name(last: str, first: str, middle: str = "") -> str:
    if middle:
        return f"{last.capitalize()} {first.capitalize()} {middle.capitalize()}"
    return f"{last.capitalize()} {first.capitalize()}"


def format_short_name(last: str, first: str) -> str:
    return f"{last.capitalize()} {first[0].upper()}."


def map_gender(gender: str) -> str:
    return "M" if gender.lower() == "male" else "F"


async def import_external_athletes(session: AsyncSession, athletes: List[Dict]) -> List[int]:
    """
    Запись атлетов в БД
    """
    inserted_ids = []

    for athlete in athletes:
        # Получаем команду
        try:
            division_id = athlete["divisionId"]
        except KeyError:
            continue
        team_result = await session.execute(
            select(ExternalTeamMapping).where(ExternalTeamMapping.external_id == division_id)
        )
        team_mapping = team_result.scalar_one_or_none()

        if not team_mapping:
            print(f"⚠️ Пропущен атлет {athlete['lastName']} — нет команды с divisionId {division_id}")
            continue

        athlete_id = athlete['id']
        # Формируем имя
        full_name = format_full_name(athlete["lastName"], athlete["firstName"], athlete.get("middleName", ""))
        short_name = format_short_name(athlete["lastName"], athlete["firstName"])
        age = athlete["age"]
        gender = map_gender(athlete["gender"])

        participant = Participant(
            participant_id=athlete_id,
            full_name=full_name,
            short_name=short_name,
            age=age,
            gender=gender,
            team_id=team_mapping.team_id
        )
        session.add(participant)
        await session.flush()  # получим participant_id

        inserted_ids.append(participant.participant_id)

        # Привязка к видам спорта
        discipline_ids = athlete.get("disciplineIds", [])
        if not discipline_ids:
            continue

        # Получаем соответствия внешних ID дисциплин
        sport_results = await session.execute(
            select(ExternalSportMapping).where(ExternalSportMapping.external_id.in_(discipline_ids))
        )
        sport_mappings = sport_results.scalars().all()

        for mapping in sport_mappings:
            participant_sport = ParticipantSport(
                participant_id=participant.participant_id,
                sport_id=mapping.sport_id
            )
            session.add(participant_sport)

    await session.commit()
    return inserted_ids


async def import_external_teams(session: AsyncSession, external_teams: List[Dict]) -> None:
    """
    Запись команд в БД
    """
    for ext_team in external_teams:
        name = ext_team["name"]
        external_id = ext_team["id"]

        # Создаём команду
        team = Team(name=name)
        session.add(team)
        await session.flush()  # Получим team_id

        # Добавляем внешний маппинг
        mapping = ExternalTeamMapping(team_id=team.team_id, external_id=external_id)
        session.add(mapping)

    await session.commit()


async def import_external_sports(session: AsyncSession, external_sports: List[Dict]) -> None:
    """
    Запись спортов в БД
    """
    for ext_sport in external_sports:
        name = ext_sport["name"]
        external_id = ext_sport["id"]

        # Создаём спорт
        sport = Sport(
            name=name,
        )
        session.add(sport)
        await session.flush()  # Получим sport_id

        # Добавляем маппинг
        mapping = ExternalSportMapping(sport_id=sport.sport_id, external_id=external_id)
        session.add(mapping)

    await session.commit()