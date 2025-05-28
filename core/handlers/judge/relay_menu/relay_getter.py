"""
Модуль геттеров для эстафеты
"""
from typing import Dict, Any
import logging

from aiogram_dialog import DialogManager

from database.relay_requests import get_last_judge_reley_results
from database.service_requests import get_teams_by_sport, get_team_name_by_id
from handlers.judge.run_menu.run_handlers import format_seconds_to_time_string

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def relay_team_choose_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    sport = dialog_manager.start_data['sport_name']

    teams = await get_teams_by_sport(sport, session)

    return {'relay_teams': [{'name': name, 'id': id_} for name, id_ in teams.items()]}


async def relay_time_register_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    relay_team_id = dialog_manager.dialog_data['relay_team_id']

    team_name = await get_team_name_by_id(session, relay_team_id)

    dialog_manager.dialog_data['relay_team_name'] = team_name

    return {'relay_team': team_name, 'distance': 'Эстафета 4х100 м'}


async def relay_time_confirm_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    distance = dialog_manager.start_data['sport_name']
    team_name = dialog_manager.dialog_data['relay_team_name']
    team_time = format_seconds_to_time_string(dialog_manager.dialog_data['relay_time'])

    return {'distance': distance, 'relay_team': team_name, 'relay_time': team_time}


async def relay_history_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    telegram_id = dialog_manager.start_data['judge_telegram_id']
    distance = dialog_manager.start_data['sport_name']

    history = await get_last_judge_reley_results(session, telegram_id)
    logger.debug(history)
    printable_data = '\n'.join([f'{result[0]} - {format_seconds_to_time_string(result[1])}' for result in history])

    return {'distance': distance, 'history': printable_data}
