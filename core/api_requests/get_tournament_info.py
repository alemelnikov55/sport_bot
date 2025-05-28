"""
Модуль для зашруки информации из внешней системы
"""
import asyncio
from pprint import pprint

from main_load_requests import get_athletes, get_divisions, get_disciplines
from inpout_requests import import_external_athletes, import_external_teams, import_external_sports

from database.models.engine import async_session


async def get_tournament_full_info():
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


if __name__ == "__main__":
    asyncio.run(get_tournament_full_info())


