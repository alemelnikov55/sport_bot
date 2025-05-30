import logging
from typing import Dict, Any

from aiogram_dialog import DialogManager

from database.models import DartsPlayoffType
from database.darts_requests import get_top_darts_qualifiers, get_playoff_match_info, get_all_playoffs_matches

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

types = DartsPlayoffType.get_data_for_chose_type()
mapped_playoff_type = DartsPlayoffType.__dict__['_member_map_']



async def darts_playoff_choose_first_player_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает список игроков для выбора первого игрока в дартс-плейофф.
    """
    session = dialog_manager.middleware_data['session']

    top_players = await get_top_darts_qualifiers(session)

    top_players_info = {
        str(player['player_id']): {
            'name': player['name'],
            'team_id': player['team_id'],
            'team_name': player['team_name'],
            # 'score': player['scores'],
        } for player in top_players}

    dialog_manager.dialog_data['darts_playoff_players'] = top_players_info

    return {'playoff_players': top_players}


async def darts_playoff_choose_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']

    playoff_matches = await get_all_playoffs_matches(session)

    return {'playoff_matches': playoff_matches}


async def darts_playoff_choose_type_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает тип плейоффа для выбора.
    """
    return {'playoff_types': types}


async def darts_playoff_confirm_start_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает информацию о первом игроке и типе матча для подтверждения начала матча.
    """
    first_player = str(dialog_manager.dialog_data['darts_playoff_first_player_id'])
    second_player = str(dialog_manager.dialog_data['darts_playoff_second_player_id'])
    match_type = dialog_manager.dialog_data['darts_playoff_type_id']

    players_data = dialog_manager.dialog_data['darts_playoff_players']

    first_player_name = players_data.get(first_player).get('name')
    second_player_name = players_data.get(second_player).get('name')
    match_type_printable = mapped_playoff_type[match_type].value

    return {'first_player_name': first_player_name,
            'second_player_name': second_player_name,
            'match_type': match_type_printable}


async def darts_playoff_process_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    playoff_id = dialog_manager.dialog_data['darts_playoff_match_id']

    match_info = await get_playoff_match_info(session, playoff_id)
    match_info['leg'] = match_info['player_1']['scores'] + match_info['player_2']['scores'] + 1

    first_player_name = match_info['player_1']['name']
    second_player_name = match_info['player_2']['name']
    first_player_id = match_info['player_1']['id']
    second_player_id = match_info['player_2']['id']

    players = [
        {'name': first_player_name, 'player_id': first_player_id},
        {'name': second_player_name, 'player_id': second_player_id},
    ]

    return {'playoff_players': players, 'match_info': match_info}
