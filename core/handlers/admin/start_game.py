from datetime import datetime
import logging

from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from database.darts_requests import get_darts_qualifiers_sorted, get_all_playoffs_matches
from database.football_requests import get_football_matches_with_goals_and_fallers
from database.kettle_requests import get_kettle_export_results
from database.models import async_session
from database.pong_requests import get_all_pong_matches_grouped
from database.relay_requests import get_relay_results
from database.run_requests import get_running_results_by_distance
from database.tug_of_war_requests import get_all_tug_matches_grouped
from database.volleyball_requests import get_all_volleyball_matches
from utils.google_supports.requests_to_google import update_multiple_sheets

logger = logging.getLogger(__name__)


async def start_game(message: Message, scheduler: AsyncIOScheduler, session: AsyncSession):
    scheduler.add_job(update_google_sheets, 'interval', minutes=1)
    await message.answer('Обновление турнирной таблицы запущено')


async def update_google_sheets():
    total_spartakiada_data = dict()

    async with async_session() as session:
        volleyball_tournament_info = await get_all_volleyball_matches(session)
        football_tournament_info = await get_football_matches_with_goals_and_fallers(session)
        pong_tournament_info = await get_all_pong_matches_grouped(session)
        run_tournament_info = await get_running_results_by_distance(session)
        tug_tournament_info = await get_all_tug_matches_grouped(session)
        relay_tournament_info = await get_relay_results(session)
        kettle_tournament_info = await get_kettle_export_results(session)
        darts_qualifiers_info = await get_darts_qualifiers_sorted(session)
        darts_playoff_info = await get_all_playoffs_matches(session)

    total_spartakiada_data['football'] = football_tournament_info
    total_spartakiada_data['volleyball'] = volleyball_tournament_info
    total_spartakiada_data['pong'] = pong_tournament_info
    total_spartakiada_data['run_100'] = run_tournament_info.get('100')
    total_spartakiada_data['run_2000'] = run_tournament_info.get('2000')
    total_spartakiada_data['run_3000'] = run_tournament_info.get('3000')
    total_spartakiada_data['relay'] = relay_tournament_info
    total_spartakiada_data['tug'] = tug_tournament_info
    total_spartakiada_data['kettle'] = kettle_tournament_info
    total_spartakiada_data['darts_qualifiers'] = darts_qualifiers_info
    total_spartakiada_data['darts_playoff'] = darts_playoff_info

    update_multiple_sheets(total_spartakiada_data)

    logger.info(f'Обновлены данные в таблице {datetime.now()}')
