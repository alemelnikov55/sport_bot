import logging
from typing import Any, Dict

from aiogram_dialog import DialogManager

from database.run_requests import get_last_judge_run_results
from handlers.judge.run_menu.run_handlers import format_seconds_to_time_string

logger = logging.getLogger(__name__)


async def run_time_register_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    distance = dialog_manager.start_data['sport_name']
    runner_id = int(dialog_manager.dialog_data['runner_id'])
    runner_name = dialog_manager.dialog_data['runner_name']

    return {'runner_name': runner_name, 'runner_id': runner_id, 'distance': distance}


async def run_time_confirm_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    distance = dialog_manager.start_data['sport_name']
    runner_id = int(dialog_manager.dialog_data['runner_id'])
    runner_name = dialog_manager.dialog_data['runner_name']
    runner_time = format_seconds_to_time_string(dialog_manager.dialog_data['runner_time'])

    return {'runner_name': runner_name, 'runner_id': runner_id, 'distance': distance, 'runner_time': runner_time}


async def run_history_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    sport_name = dialog_manager.start_data['sport_name']
    telegram_id = dialog_manager.start_data['judge_telegram_id']

    # distance = int(sport_name.split('_')[-1][:-1])
    distance = int(sport_name.split(' ')[-2])

    data = await get_last_judge_run_results(session, telegram_id, distance)
    printable_data = [f'{result[0]}_{result[1]}  -  {format_seconds_to_time_string(result[2])}' for result in data]
    return {'history': '\n'.join(printable_data), 'distance': distance}
