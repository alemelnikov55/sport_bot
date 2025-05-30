import logging
from typing import Dict, Any

from aiogram_dialog import DialogManager

from database.kettle_requests import get_judge_history
from database.service_requests import get_teams_by_sport, get_team_participants_by_team_and_sport

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CATEGORY = {
    'M': ['до 73', 'до 85', '85+'],
    'F': ['0-100+']
}


async def kettle_team_choose_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    sport_id = dialog_manager.start_data['sport_id']

    teams = await get_teams_by_sport(sport_id, session)

    return {'kettle_teams': [{'name': name, 'id': id_} for name, id_ in teams.items()]}


async def kettle_choose_lifter_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    team_id = dialog_manager.dialog_data['kettle_team_id']
    sport_id = dialog_manager.start_data['sport_id']

    players = await get_team_participants_by_team_and_sport(team_id, sport_id, session)

    return {'players': [{'name': f'{name.split(' ')[0]} {id_}', 'id': id_} for name, id_ in players.items()]}


# async def kettle_choose_category_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
#     gender = dialog_manager.dialog_data['kettle_lifter']['gender']
#     categories = CATEGORY[gender]
#     return {'categories': [{'category': category} for category in categories]}


async def kettle_count_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    lifter_info = dialog_manager.dialog_data['kettle_lifter']
    weight = dialog_manager.dialog_data['lifter_weight']
    return {'lifter_name': lifter_info['name'], 'weight': weight, 'age': lifter_info['age']}


async def kettle_confirm_result_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    lifter_info = dialog_manager.dialog_data['kettle_lifter']
    weight = dialog_manager.dialog_data['lifter_weight']
    lift_count = dialog_manager.dialog_data['lift_count']
    return {'lifter_name': lifter_info['name'], 'weight': weight, 'lift_count': lift_count}


async def kettle_history_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    telegram_id = dialog_manager.start_data['judge_telegram_id']
    history_results = []

    results = await get_judge_history(session, telegram_id)

    for result in results:
        infoline = f'<b>{result['short_name']}</b>  в  {result['weight']}:  {result['lift_count']}'
        history_results.append(infoline)

    return {'history': '\n'.join(history_results)}
