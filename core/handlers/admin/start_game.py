from datetime import datetime

from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import get_football_matches_with_goals
from utils.google_supports.requests_to_google import update_google_sheet


async def start_game(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    scheduler.add_job(update_google_sheets, 'interval', minutes=1)
    await message.answer('Обновление турнирной таблицы запущено')


async def update_google_sheets():
    goals = await get_football_matches_with_goals()
    # print(goals)
    update_google_sheet(goals)
    print(f'Обновлены данные в таблице {datetime.now()}')
