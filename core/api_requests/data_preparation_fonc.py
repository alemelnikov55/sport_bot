import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from typing import Type, Callable, Any, List, Dict

from api_requests.final_table_getters import DartsPlaceCalculator, prepare_kettlebell_men_api_payload, \
    prepare_kettlebell_women_api_payload, calculate_tug_of_war_places, TableTennisPlaceCalculator
from database.models import (
    ExternalSportMapping, Sport, ExternalTeamMapping, VolleyballMatch, FootballMatch, RunningResult
)
from database.models.relay_race_model import RelayResult

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
# VOLLEYBALL STAGES
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
    """Создает payload для сетки волейбольного турнира"""
    return await build_generic_tournament_data(
        session=session,
        match_model=VolleyballMatch,
        sport_name="Волейбол",
        extract_status=status_mapper,
        get_match_info=volleyball_match_info
    )


# ===========================================
# FOOTBALL STAGES
# ===========================================
def football_match_info(match, team_map):
    """
    Создает
    """
    return {
        "id": str(match.match_id),
        "participants": [
            {"divisionId": team_map[match.team1_id]},
            {"divisionId": team_map[match.team2_id]}
        ]
    }


async def build_football_tournament_data(session: AsyncSession):
    """Создает payload для сетки футбольного турнира"""
    return await build_generic_tournament_data(
        session=session,
        match_model=FootballMatch,
        sport_name="Мини-Футбол",
        extract_status=status_mapper,
        get_match_info=football_match_info
    )


class BaseResultPayloadBuilder:
    """Базовый класс для создания payload для результатов соревнований"""
    sport_name: str  # "Бег 100 м", "Эстафета 4х100 м" и т.п.

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_discipline_id(self) -> str:
        sport_id = await self.session.scalar(
            select(Sport.sport_id).where(Sport.name.ilike(self.sport_name))
        )
        if not sport_id:
            raise ValueError(f"❌ Спорт '{self.sport_name}' не найден")

        external_id = await self.session.scalar(
            select(ExternalSportMapping.external_id).where(ExternalSportMapping.sport_id == sport_id)
        )
        if not external_id:
            raise ValueError(f"❌ Внешний ID для '{self.sport_name}' не найден")

        return external_id

    async def build(self) -> dict:
        """Метод для создания payload, готовой к отправке"""
        discipline_id = await self.get_discipline_id()
        results = await self.collect_results()
        return {
            "correlationId": str(uuid.uuid4()),
            "disciplineId": discipline_id,
            "results": results
        }

    async def collect_results(self) -> List[Dict[str, Any]]:
        """Переопределяется в подклассах"""
        raise NotImplementedError("Переопредели collect_results() в наследнике")


class RunningResultBuilder(BaseResultPayloadBuilder):
    """Базовый класс для создания payload для результатов п бегу"""
    sport_name = ""  # будет задаваться динамически

    def __init__(self, session: AsyncSession, distance_m: int):
        super().__init__(session)
        self.distance_m = distance_m
        self.sport_name = f"Бег {distance_m} м"

    async def collect_results(self):
        rows = await self.session.execute(
            select(RunningResult).where(RunningResult.distance_m == self.distance_m)
        )
        results = rows.scalars().all()
        return [
            {
                "athleteId": r.participant_id,
                "result": int(float(r.result_time) * 1000)
            }
            for r in results
        ]


class RelayResultBuilder(BaseResultPayloadBuilder):
    """класс для создания payload для результатов эстафеты"""
    sport_name = "Эстафета 4 х 100 м"

    async def collect_results(self):
        # Получаем маппинг team_id → external divisionId
        rows = await self.session.execute(select(ExternalTeamMapping))
        team_map = {r.team_id: r.external_id for r in rows.scalars()}

        results_query = await self.session.execute(select(RelayResult))
        results = results_query.scalars().all()

        payload = []
        for r in results:
            ext_id = team_map.get(r.team_id)
            if ext_id:
                payload.append({
                    "divisionId": ext_id,
                    "result": int(float(r.result_time) * 1000)
                })
        return payload


class FootballResultBuilder(BaseResultPayloadBuilder):
    """класс для создания payload для результатов футбольного матча"""
    sport_name = "Мини-Футбол"

    async def build_for_match(self, match_id: int) -> Dict[str, Any]:
        """
        Возвращает payload для конкретного матча по футболу
        """
        # Получаем external_id команд
        team_rows = await self.session.execute(select(ExternalTeamMapping))
        team_map = {t.team_id: t.external_id for t in team_rows.scalars()}

        # Получаем конкретный матч
        match = await self.session.scalar(
            select(FootballMatch).where(FootballMatch.match_id == match_id)
        )

        if not match:
            raise ValueError(f"❌ Матч с id={match_id} не найден")

        ext_team1 = team_map.get(match.team1_id)
        ext_team2 = team_map.get(match.team2_id)

        if not ext_team1 or not ext_team2:
            raise ValueError(f"❌ Нет external_id у одной из команд матча {match_id}")

        return {
            "correlationId": str(uuid.uuid4()),
            "disciplineId": await self.get_discipline_id(),
            "competitionId": str(match.match_id),
            "results": [
                {"divisionId": ext_team1, "result": match.score1},
                {"divisionId": ext_team2, "result": match.score2}
            ]
        }


class VolleyballResultBuilder(BaseResultPayloadBuilder):
    """класс для создания payload для результатов волейбольного матча"""
    sport_name = "Волейбол"

    async def build_for_match(self, match_id: int) -> Dict[str, Any]:
        """
        Возвращает payload для конкретного матча по волейболу
        """
        team_rows = await self.session.execute(select(ExternalTeamMapping))
        team_map = {t.team_id: t.external_id for t in team_rows.scalars()}

        match = await self.session.scalar(
            select(VolleyballMatch).where(VolleyballMatch.match_id == match_id)
        )
        # if not match:
        #     raise ValueError(f"❌ Матч с id={match_id} не найден")

        ext_team1 = team_map.get(match.team1_id)
        ext_team2 = team_map.get(match.team2_id)

        # if not ext_team1 or not ext_team2:
        #     raise ValueError(f"❌ Нет external_id у одной из команд матча {match_id}")

        return {
            "correlationId": str(uuid.uuid4()),
            "disciplineId": await self.get_discipline_id(),
            "competitionId": str(match.match_id),
            "results": [
                {"divisionId": ext_team1, "result": match.team1_set_wins},
                {"divisionId": ext_team2, "result": match.team2_set_wins}
            ]
        }


class DartsResultBuilder(BaseResultPayloadBuilder):
    sport_name = "Дартс"

    async def collect_results(self) -> List[Dict[str, Any]]:
        placer = DartsPlaceCalculator(self.session)
        places_by_gender = await placer.calculate_places()
        payload = []
        for gender_group in places_by_gender.values():
            for entry in gender_group:
                athlete_id = entry["participant_id"]
                raw_place = entry["place"]
                try:
                    place_value = int(raw_place.split("-")[0])
                except ValueError:
                    continue
                payload.append({
                    "athleteId": athlete_id,
                    "result": place_value
                })

        return payload

    async def build(self) -> dict:
        discipline_id = await self.get_discipline_id()
        results = await self.collect_results()
        return {
            "correlationId": str(uuid.uuid4()),
            "disciplineId": discipline_id,
            "results": results
        }


class KettlebellResultBuilder(BaseResultPayloadBuilder):
    sport_name = "Гиревой спорт"

    async def collect_results(self) -> List[Dict[str, Any]]:
        man_result = await prepare_kettlebell_men_api_payload(self.session)
        women_result = await prepare_kettlebell_women_api_payload(self.session)
        man_result.extend(women_result)
        return man_result

    async def build(self) -> Dict[str, Any]:
        return {
            "correlationId": str(uuid.uuid4()),
            "disciplineId": await self.get_discipline_id(),
            "results": await self.collect_results()
        }


class TugResultBuilder(BaseResultPayloadBuilder):
    sport_name = "Перетягивание каната"

    async def collect_results(self, playoff_teams_count: int=4) -> List[Dict[str, Any]]:
        results = await calculate_tug_of_war_places(self.session, playoff_teams_count)
        return results

    async def build(self, playoff_teams_count) -> Dict[str, Any]:
        return {
            "correlationId": str(uuid.uuid4()),
            "disciplineId": await self.get_discipline_id(),
            "results": await self.collect_results(playoff_teams_count)
        }


class TableTennisResultBuilder(BaseResultPayloadBuilder):
    sport_name = "Настольный теннис"

    async def collect_results(self) -> List[Dict[str, Any]]:
        placer = TableTennisPlaceCalculator(self.session)
        place_dict = await placer.calculate_places()

        result_payload = []
        for gender in ("M", "F"):
            for row in place_dict.get(gender, []):
                result_payload.append({
                    "athleteId": row["participant_id"],
                    "result": row["place"]  # строка: "1", "2", "5-6" и т.д.
                })

        return result_payload

    async def build(self) -> Dict[str, Any]:
        return {
            "correlationId": str(uuid.uuid4()),
            "disciplineId": await self.get_discipline_id(),
            "results": await self.collect_results()
        }