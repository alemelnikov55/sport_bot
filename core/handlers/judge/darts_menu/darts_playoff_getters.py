import logging
import time
from typing import Dict, Any

from aiogram_dialog import DialogManager

from database.models import DartsPlayoffType
from database.darts_requests import get_top_darts_qualifiers

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

types = DartsPlayoffType.get_data_for_chose_type()
mapped_playoff_type = DartsPlayoffType.__dict__['_member_map_']
# print(DartsPlayoffType.__dict__)


async def darts_playoff_choose_first_player_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """
    Получает список игроков для выбора первого игрока в дартс-плейофф.
    """
    session = dialog_manager.middleware_data['session']
    logger.debug('darts_playoff_choose_first_player_getter')
    start = time.monotonic()

    top_players = await get_top_darts_qualifiers(session)
    logger.debug(f'time {time.monotonic() - start}')

    top_players_info = {
        str(player['player_id']): {
        'name': player['name'],
        'team_id': player['team_id'],
        'team_name': player['team_name'],
        # 'score': player['scores'],
    } for player in top_players}

    dialog_manager.dialog_data['darts_playoff_players'] = top_players_info
    logger.debug(top_players_info)

    return {'playoff_players': top_players}


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