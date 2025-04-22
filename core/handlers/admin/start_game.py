from datetime import datetime
import logging

from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import get_football_matches_with_goals_and_fallers
from database.models import async_session
from database.pong_requests import get_all_pong_matches_grouped
from database.volleyball_requests import get_active_volleyball_matches
from utils.google_supports.requests_to_google import update_multiple_sheets

logger = logging.getLogger(__name__)


async def start_game(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    scheduler.add_job(update_google_sheets, 'interval', minutes=1)
    await message.answer('Обновление турнирной таблицы запущено')


async def update_google_sheets():
    total_spartakiada_data = dict()

    async with async_session() as session:
        volleyball_tournament_info = await get_active_volleyball_matches(session)
        football_tournament_info = await get_football_matches_with_goals_and_fallers(session)
        pong_tournament_info = await get_all_pong_matches_grouped(session)

    total_spartakiada_data['football'] = football_tournament_info
    total_spartakiada_data['volleyball'] = volleyball_tournament_info
    total_spartakiada_data['pong'] = pong_tournament_info
    update_multiple_sheets(total_spartakiada_data)

    logger.info(f'Обновлены данные в таблице {datetime.now()}')
