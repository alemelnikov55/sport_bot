from typing import Dict, Any
import logging

from aiogram_dialog import DialogManager

from database.service_requests import get_teams_by_sport
from database.tug_of_war_requests import get_tug_matches, get_tug_match_info_by_id, \
    get_tug_match_info_for_process_by_id
from loader import groups_type

logger = logging.getLogger(__name__)


async def tug_matches_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']

    pulls = await get_tug_matches(session)

    return {'tug_matches': pulls}


async def start_tug_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    pull_id = dialog_manager.dialog_data['pull_id']

    match_info = await get_tug_match_info_by_id(session, pull_id)

    return {'tug_match': match_info}


async def tug_match_info_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    pull_id = dialog_manager.dialog_data['pull_id']

    match_info = await get_tug_match_info_for_process_by_id(session, pull_id)

    only_teams_info = [{'team_id': match_info['team1_id'], 'team_name': match_info['team1_name']},
                       {'team_id': match_info['team2_id'], 'team_name': match_info['team2_name']}]

    return {'tug_match': match_info, 'only_teams_info': only_teams_info}


async def tug_finish_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    pull_id = dialog_manager.dialog_data['pull_id']

    match_info = await get_tug_match_info_for_process_by_id(session, pull_id)

    return {'tug_match': match_info}


async def tug_teams_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    sport = dialog_manager.start_data['sport_name']

    teams = await get_teams_by_sport(sport, session)

    formatted_teams = [{'name': name, 'id': id_} for name, id_ in teams.items()]

    return {'tug_teams': formatted_teams}


async def tug_set_group_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    return {'groups': groups_type}
