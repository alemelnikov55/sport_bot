from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Union, Any, Set, Sequence
from collections import defaultdict

from database.models import TugOfWarMatch, ExternalTeamMapping, DartsPlayOff, Participant, KettleResult
from database.models.pong_models import TableTennisMatch

PLAYOFF_ORDER = ["Фин", "За 3", "1/2", "1/4", "1/8"]

PLAYOFF_PRIORITY = {
    "FINAL": 1,
    "THIRD_PLACE": 2,
    "ONE_HALF": 3,
    "ONE_QUARTER": 4,
    "ONE_EIGHTH": 5,
}

async def calculate_tug_of_war_places(session: AsyncSession, playoff_team_count: int = 8) -> List[Dict[str, Union[str]]]:
    result: List[Dict[str, Union[str]]] = []
    assigned_teams = set()

    # Получаем карту team_id → external_id
    team_rows = await session.execute(select(ExternalTeamMapping))
    team_map = {t.team_id: t.external_id for t in team_rows.scalars()}

    # Загружаем все матчи
    tug_matches = await session.scalars(select(TugOfWarMatch))
    matches = tug_matches.all()

    playoff_matches = defaultdict(list)
    qualification_matches = []

    for match in matches:
        if match.group_name in PLAYOFF_ORDER:
            playoff_matches[match.group_name].append(match)
        elif match.group_name and match.group_name.isalpha():
            qualification_matches.append(match)

    place_map: Dict[str, str] = {}

    # Финал
    for match in playoff_matches.get("Фин", []):
        winner = match.team1_id if match.score1 > match.score2 else match.team2_id
        loser = match.team2_id if match.score1 > match.score2 else match.team1_id
        w_ext = team_map.get(winner)
        l_ext = team_map.get(loser)
        if w_ext and l_ext:
            place_map[w_ext] = "1"
            place_map[l_ext] = "2"
            assigned_teams.update([winner, loser])

    # За 3
    for match in playoff_matches.get("За 3", []):
        winner = match.team1_id if match.score1 > match.score2 else match.team2_id
        loser = match.team2_id if match.score1 > match.score2 else match.team1_id
        w_ext = team_map.get(winner)
        l_ext = team_map.get(loser)
        if w_ext and l_ext:
            place_map[w_ext] = "3"
            place_map[l_ext] = "4"
            assigned_teams.update([winner, loser])

    # Остальные стадии
    for stage in ["1/2", "1/4", "1/8"]:
        stage_matches = playoff_matches.get(stage, [])
        losers = []
        for match in stage_matches:
            loser = match.team2_id if match.score1 > match.score2 else match.team1_id
            if loser not in assigned_teams:
                losers.append(loser)

        if losers:
            max_place = playoff_team_count
            for s in PLAYOFF_ORDER:
                if s == stage:
                    break
                max_place //= 2
            min_place = max_place // 2 + 1
            place_range = f"{min_place}-{max_place}"
            for team_id in losers:
                ext_id = team_map.get(team_id)
                if ext_id:
                    place_map[ext_id] = place_range
                    assigned_teams.add(team_id)

    # Квалификация
    qualifier_scores = defaultdict(int)
    for match in qualification_matches:
        if match.team1_id not in assigned_teams:
            qualifier_scores[match.team1_id] += match.score1
        if match.team2_id not in assigned_teams:
            qualifier_scores[match.team2_id] += match.score2

    if qualifier_scores:
        sorted_qualifiers = sorted(qualifier_scores.items(), key=lambda x: x[1], reverse=True)
        total_qualifiers = len(sorted_qualifiers)
        start_place = playoff_team_count + 1
        end_place = playoff_team_count + total_qualifiers
        qual_place = f"{start_place}-{end_place}"
        for team_id, _ in sorted_qualifiers:
            ext_id = team_map.get(team_id)
            if ext_id:
                place_map[ext_id] = qual_place

    for ext_id, place in place_map.items():
        result.append({"divisionId": ext_id, "result": place})

    return result


class BaseDuelSportPlacer:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_matches(self) -> List[Any]:
        raise NotImplementedError()

    async def get_participants_map(self) -> Dict[int, str]:
        rows = await self.session.execute(select(Participant))
        return {p.participant_id: p.gender for p in rows.scalars()}

    async def calculate_places(self) -> Dict[str, List[Dict[str, Union[int, str]]]]:
        participants_gender = await self.get_participants_map()
        matches = await self.fetch_matches()

        # Победы по участнику
        wins: Dict[int, int] = {}
        for match in matches:
            winner_id = getattr(match, "winner_id", None)
            if not winner_id:
                continue
            wins[winner_id] = wins.get(winner_id, 0) + 1

        # Группировка по полу
        gender_groups: Dict[str, List[tuple]] = {"M": [], "F": []}
        for pid, count in wins.items():
            gender = participants_gender.get(pid)
            if gender in gender_groups:
                gender_groups[gender].append((pid, count))

        # Расчёт мест с учётом делений
        result = {"M": [], "F": []}
        for gender, group in gender_groups.items():
            sorted_group = sorted(group, key=lambda x: -x[1])
            rank_list = []
            prev_score = None
            current_place = 1
            index = 0

            while index < len(sorted_group):
                tied = [sorted_group[index]]
                score = sorted_group[index][1]

                # собираем всех с одинаковым счетом
                j = index + 1
                while j < len(sorted_group) and sorted_group[j][1] == score:
                    tied.append(sorted_group[j])
                    j += 1

                # определяем место
                if len(tied) == 1:
                    place = str(current_place)
                else:
                    place = f"{current_place}-{current_place + len(tied) - 1}"

                for pid, _ in tied:
                    rank_list.append({"participant_id": pid, "place": place})

                current_place += len(tied)
                index = j

            result[gender] = rank_list

        return result


class DartsPlaceCalculator:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_participant_genders(self) -> Dict[int, str]:
        result = await self.session.execute(select(Participant))
        return {p.participant_id: p.gender for p in result.scalars().all()}

    async def calculate_places(self) -> Dict[str, List[Dict[str, Union[int, str]]]]:
        gender_map = await self.get_participant_genders()
        result = {"M": [], "F": []}
        assigned: Dict[int, str] = {}

        matches = await self.session.scalars(
            select(DartsPlayOff).where(DartsPlayOff.winner_id.isnot(None))
        )
        matches = sorted(matches.all(), key=lambda m: PLAYOFF_PRIORITY.get(m.playoff_type, 99))
        # Финал и матч за 3-е место
        for match in matches:
            match_type = match.playoff_type.name
            p1, p2 = match.player1_id, match.player2_id
            winner, loser = match.winner_id, p2 if match.winner_id == p1 else p1

            if match_type == "FINAL":
                assigned[winner] = "1"
                assigned[loser] = "2"
            elif match_type == "THIRD_PLACE":
                assigned[winner] = "3"
                assigned[loser] = "4"

        # 1/2 финала проигравшие
        for match in matches:
            match_type = match.playoff_type.name
            if match_type == "ONE_HALF":
                loser = match.player2_id if match.winner_id == match.player1_id else match.player1_id
                if loser not in assigned:
                    assigned[loser] = "5-6"

        # 1/4 финала проигравшие
        for match in matches:
            match_type = match.playoff_type.name
            if match_type == "ONE_QUARTER":
                loser = match.player2_id if match.winner_id == match.player1_id else match.player1_id
                if loser not in assigned:

                    assigned[loser] = "7-10"

        # Группировка по полу
        for participant_id, place in assigned.items():
            gender = gender_map.get(participant_id)
            if gender in result:
                result[gender].append({
                    "participant_id": participant_id,
                    "place": place
                })

        return result


class TableTennisPlaceCalculator:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.PLAYOFF_ORDER = ["Фин", "За 3", "1/2", "1/4", "1/8"]  # Порядок важности матчей
        self.BASE_PLACE_RANGES = {
            "Фин": {"winner": "1", "loser": "2"},
            "За 3": {"winner": "3", "loser": "4"},
            "1/2": {"loser": "5-8"},
            "1/4": {"loser": "9-16"},
            "1/8": {"loser": "17-32"}
        }

    async def get_participant_genders(self) -> Dict[int, str]:
        result = await self.session.execute(select(Participant))
        return {p.participant_id: p.gender for p in result.scalars().all()}

    async def get_all_participants(self) -> List[int]:
        result = await self.session.execute(select(Participant.participant_id))
        return [r[0] for r in result.all()]

    async def get_playoff_depth(self, matches: Sequence[TableTennisMatch]) -> str:
        """Определяет глубину плей-оффа (1/2, 1/4 или 1/8)"""
        playoff_types = {m.group_name for m in matches if m.group_name in self.PLAYOFF_ORDER}

        if "1/8" in playoff_types:
            return "1/8"
        elif "1/4" in playoff_types:
            return "1/4"
        elif "1/2" in playoff_types:
            return "1/2"
        return ""

    async def calculate_places(self) -> Dict[str, List[Dict[str, Union[int, str]]]]:
        gender_map = await self.get_participant_genders()
        all_participants = await self.get_all_participants()
        total_participants = len(all_participants)
        result = {"M": [], "F": []}
        assigned: Dict[int, str] = {}
        playoff_participants: Set[int] = set()

        # Получаем все завершенные матчи плей-оффа
        playoff_matches = await self.session.scalars(
            select(TableTennisMatch).where(
                TableTennisMatch.winner_id.isnot(None),
                TableTennisMatch.group_name.in_(self.PLAYOFF_ORDER)
            )
        )
        playoff_matches = playoff_matches.all()

        # Определяем глубину плей-оффа
        playoff_depth = await self.get_playoff_depth(playoff_matches)

        # Сортируем матчи по важности
        playoff_matches_sorted = sorted(
            playoff_matches,
            key=lambda m: self.PLAYOFF_ORDER.index(m.group_name) if m.group_name in self.PLAYOFF_ORDER else len(
                self.PLAYOFF_ORDER)
        )

        # Обрабатываем матчи плей-оффа
        for match in playoff_matches_sorted:
            p1, p2 = match.player1_id, match.player2_id
            winner, loser = match.winner_id, p2 if match.winner_id == p1 else p1

            playoff_participants.update([p1, p2])

            if match.group_name in self.BASE_PLACE_RANGES:
                place_info = self.BASE_PLACE_RANGES[match.group_name]

                if "winner" in place_info and winner not in assigned:
                    assigned[winner] = place_info["winner"]

                if "loser" in place_info and loser not in assigned:
                    assigned[loser] = place_info["loser"]

        # Корректируем места в зависимости от глубины плей-оффа
        if playoff_depth == "1/2":
            # Если плей-офф начинался с 1/2, то проигравшие в 1/2 получают 3-4 места
            for match in playoff_matches_sorted:
                if match.group_name == "1/2":
                    loser = match.player2_id if match.winner_id == match.player1_id else match.player1_id
                    if loser not in assigned:
                        assigned[loser] = "3-4"
        elif playoff_depth == "1/4":
            # Если плей-офф начинался с 1/4, то проигравшие в 1/4 получают 5-8 места
            for match in playoff_matches_sorted:
                if match.group_name == "1/4":
                    loser = match.player2_id if match.winner_id == match.player1_id else match.player1_id
                    if loser not in assigned:
                        assigned[loser] = "5-8"

        # Обрабатываем отборочные матчи (group_name из 1 буквы)
        qualifying_matches = await self.session.scalars(
            select(TableTennisMatch).where(
                TableTennisMatch.winner_id.isnot(None),
                TableTennisMatch.group_name.isnot(None),
                TableTennisMatch.group_name.regexp_match('^[A-Za-z]$')
            )
        )

        # Собираем участников отборочных
        qualifying_participants = set()
        for match in qualifying_matches:
            qualifying_participants.update([match.player1_id, match.player2_id])

        # Определяем участников, не прошедших в плей-офф
        non_playoff_participants = [
            p for p in qualifying_participants
            if p not in assigned and p in all_participants
        ]

        # Определяем участников, не игравших ни в одном матче
        non_participants = [
            p for p in all_participants
            if p not in assigned and p not in qualifying_participants
        ]

        # Все участники, не прошедшие в плей-офф (игравшие в отборочных или не игравшие вообще)
        all_non_playoff = non_playoff_participants + non_participants

        # Определяем диапазон мест для не прошедших в плей-офф
        if all_non_playoff:
            # Находим максимальное место в плей-оффе
            max_playoff_place = 0
            for place in assigned.values():
                if '-' in place:
                    current_max = int(place.split('-')[-1])
                else:
                    current_max = int(place)
                if current_max > max_playoff_place:
                    max_playoff_place = current_max

            # Формируем диапазон мест для не прошедших
            start_place = max_playoff_place + 1
            end_place = total_participants
            common_place = f"{start_place}-{end_place}"

            # Присваиваем этот диапазон всем не прошедшим
            for participant in all_non_playoff:
                assigned[participant] = common_place

        # Группируем результаты по полу
        for participant_id, place in assigned.items():
            gender = gender_map.get(participant_id)
            if gender in result:
                result[gender].append({
                    "participant_id": participant_id,
                    "place": place
                })

        return result


######################################
#  KETTLEBELL
######################################
async def prepare_kettlebell_men_api_payload(session: AsyncSession):
    stmt = (
        select(
            KettleResult.lifter_id,
            KettleResult.weight,
            func.max(KettleResult.lift_count).label("max_lift")
        )
        .join(Participant, Participant.participant_id == KettleResult.lifter_id)
        .where(Participant.gender == 'M')
        .group_by(KettleResult.lifter_id, KettleResult.weight)
    )

    result = await session.execute(stmt)
    rows = result.all()

    return [
        {
            "athleteId": lifter_id,
            "result": lift_count,
            "weight": weight
        }
        for lifter_id, weight, lift_count in rows
        if weight is not None
    ]


async def prepare_kettlebell_women_api_payload(session: AsyncSession):
    stmt = (
        select(
            KettleResult.lifter_id,
            Participant.short_name,
            KettleResult.lift_count,
            KettleResult.weight
        )
        .join(Participant, Participant.participant_id == KettleResult.lifter_id)
        .where(Participant.gender == 'F')
    )

    result = await session.execute(stmt)
    rows = result.all()

    score_map = {}

    for lifter_id, _, lift_count, weight in rows:
        if weight is None or weight == 0:
            continue
        score = ((lift_count * 1.5) / weight) * 100
        if lifter_id not in score_map or score > score_map[lifter_id]['result']:
            score_map[lifter_id] = {
                "athleteId": lifter_id,
                "result": round(score, 2),
                "weight": weight
            }

    return list(score_map.values())
