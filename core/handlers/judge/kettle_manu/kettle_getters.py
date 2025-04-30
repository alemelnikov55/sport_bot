import logging
from typing import Dict, Any

from aiogram_dialog import DialogManager

from database.service_requests import get_teams_by_sport, get_team_participants_by_team_and_sport

logger = logging.getLogger(__name__)


async def kettle_team_choose_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    sport = dialog_manager.start_data['sport_name']

    teams = await get_teams_by_sport(sport, session)

    return {'kettle_teams': [{'name': name, 'id': id_} for name, id_ in teams.items()]}


async def kettle_choose_lifter_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    team_id = dialog_manager.dialog_data['kettle_team_id']

    players = await get_team_participants_by_team_and_sport(team_id, 'pong', session)
    logger.warning(f'kettle_players {players}')
    return {'players': [{'name': f'{name.split(' ')[0]} {id_}', 'id': id_} for name, id_ in players.items()]}