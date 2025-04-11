from datetime import datetime

from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import get_football_matches_with_goals_and_fallers
from database.models import async_session
from database.volleyball_requests import get_active_volleyball_matches
from utils.google_supports.requests_to_google import update_multiple_sheets


async def start_game(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    scheduler.add_job(update_google_sheets, 'interval', minutes=1)
    await message.answer('Обновление турнирной таблицы запущено')


async def update_google_sheets():
    total_spartakiada_data = dict()
    football_tournament_info = await get_football_matches_with_goals_and_fallers()
    async with async_session() as session:
        volleyball_tournament_info = await get_active_volleyball_matches(session)
    # print(goals)
    total_spartakiada_data['football'] = football_tournament_info
    total_spartakiada_data['volleyball'] = volleyball_tournament_info
    print(total_spartakiada_data)
    update_multiple_sheets(total_spartakiada_data)
    print(f'Обновлены данные в таблице {datetime.now()}')
