from typing import Dict, Any
import logging

from aiogram_dialog import DialogManager

from database.pong_requests import get_pong_matches, get_pong_match_info_by_id, get_current_table_tennis_match_info, \
    get_pong_match_full_info
from database.service_requests import get_teams_by_sport, get_team_participants_by_sport

logger = logging.getLogger(__name__)


def format_pong_match_info(data: dict) -> str:
    """
    Функция для формирования текста с информацией о матче по волейболу.
    :param data:
    :return:
    """
    team1 = data['player1']
    team2 = data['player2']
    sets = data["sets"]

    result = []
    result.append(f"Матч: {team1['name']} vs {team2['name']}")
    result.append(f"Счёт по сетам: {team1['sets_won']} : {team2['sets_won']}")
    result.append("")

    for set_ in sets:
        result.append(
            f"Сет {set_['set_number']}: {set_['player1_score']} - {set_['player2_score']} "
            f"({'завершён' if set_['status'] == 'finished' else 'не начат' if set_['status'] == 'not_started' else 'в процессе'})"
        )

    return "\n".join(result)


async def pong_matches_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    pong_matches = await get_pong_matches(session)
    return {'pong_matches': pong_matches}


async def pong_start_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])

    match_info = await get_pong_match_info_by_id(session, match_id)

    return {'pong_match': match_info}


async def pong_set_info_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])
    set_number = dialog_manager.dialog_data['pong_set_number']

    full_match_data = await get_current_table_tennis_match_info(session, match_id, set_number)

    team_score_data = {'player1_name': full_match_data[0]['player_name'],
                       'player1_score': full_match_data[0]['sets_won'],
                       'player2_name': full_match_data[1]['player_name'],
                       'player2_score': full_match_data[1]['sets_won'],
                       'player1_set_score': full_match_data[0]['current_set_score'],
                       'player2_set_score': full_match_data[1]['current_set_score'],
                       }

    return {'pong_match': full_match_data, 'team_score_data': team_score_data, 'set_number': set_number}


async def finish_pong_set_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])
    set_number = int(dialog_manager.dialog_data['pong_set_number'])

    full_match_data = await get_current_table_tennis_match_info(session, match_id, set_number)

    team_score_data = {'player1_name': full_match_data[0]['player_name'],
                       'player1_score': full_match_data[0]['current_set_score'],
                       'player2_name': full_match_data[1]['player_name'],
                       'player2_score': full_match_data[1]['current_set_score'], }
    logger.info(f'team_score_data {team_score_data}')
    return {'pong_set': team_score_data, 'pong_set_number': set_number}


async def pong_match_result_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])
    logger.warning(f'test match id  dialog_manager.dialog_data["volleyball_match"]')

    match_full_data = await get_pong_match_full_info(session, match_id)

    formated_text = format_pong_match_info(match_full_data)

    return {'match_result': formated_text}


async def pong_teams_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']

    pong_teams = await get_teams_by_sport('pong', session)
    logger.warning(f'volleyball_teams {pong_teams}')

    return {'teams': [{'name': name, 'id': id_} for name, id_ in pong_teams.items()]}


async def pong_players_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    team_id = int(dialog_manager.dialog_data['pong_manual_team1_id'])

    players = await get_team_participants_by_sport(team_id, 'pong', session)
    logger.warning(f'pong_players {players}')
    return {'players': [{'name': f'{name.split(' ')[0]} {id_}', 'id': id_} for name, id_ in players.items()]}

