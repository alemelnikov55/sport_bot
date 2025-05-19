"""
Модуль для зашруки информации из внешней системы
"""
import asyncio
from pprint import pprint

from main_load_requests import get_athletes, get_divisions, get_disciplines
from inpout_requests import import_external_athletes, import_external_teams, import_external_sports

from database.models.engine import async_session


async def main_api():
    athletes = get_athletes()
    teams = get_divisions()
    sports = get_disciplines()

    pprint(teams)
    pprint(sports)

    async with async_session() as session:
        # 2. Импортируем команды
        print("🔄 Импортируем команды...")
        await import_external_teams(session, teams)

        # 3. Импортируем виды спорта
        print("🔄 Импортируем виды спорта...")
        await import_external_sports(session, sports)

         # 1. Импортируем атлетов
        print("🔄 Импортируем атлетов...")
        await import_external_athletes(session, athletes)

#
# if __name__ == "__main__":
#
#     asyncio.run(main_api())

# create_tournament_stages_request = [{"disciplineId":"507f1f77bcf86cd799439011","tournament":[{"competitions":[{"id":"68000ff8fa9fb49584df8000","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{"divisionId":"507f1f77bcf86cd799439018"}],"status":"ended"}],"stage":"1/4"},{"competitions":[{"id":"68000ff8fa9fb49584df8001","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{"divisionId":"507f1f77bcf86cd799439018"}],"status":"ongoing"},{"id":"68000ff8fa9fb49584df8002","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{"divisionId":"507f1f77bcf86cd799439018"}],"status":"planned"}],"stage":"1/2"},{"competitions":[{"id":"68000ff8fa9fb49584df8003","participants":[{"divisionId":"507f1f77bcf86cd799439015"},{}],"status":"upcoming"}],"stage":"Финал"}]}] # CreateTournamentStagesRequest |
#
# pprint(create_tournament_stages_request)

