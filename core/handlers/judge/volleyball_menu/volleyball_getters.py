from typing import Any, Dict

from aiogram_dialog import DialogManager

from loader import groups_type
from database.service_requests import get_teams_by_sport
from database.volleyball_requests import get_volleyball_matches, get_volleyball_match_info_by_id, \
    get_current_volleyball_match_info, get_volleyball_match_full_info


def format_volleyball_match_info(data: dict) -> str:
    """
    Функция для формирования текста с информацией о матче по волейболу.
    :param data:
    :return:
    """
    team1 = data["team1"]
    team2 = data["team2"]
    sets = data["sets"]

    result = []
    result.append(f"Матч: {team1['name']} vs {team2['name']}")
    result.append(f"Счёт по сетам: {team1['sets_won']} : {team2['sets_won']}")
    result.append("")

    for set_ in sets:
        result.append(
            f"Сет {set_['set_number']}: {set_['team1_score']} - {set_['team2_score']} "
            f"({'завершён' if set_['status'] == 'finished' else 'не начат' if set_['status'] == 'not_started' else 'в процессе'})"
        )

    return "\n".join(result)


async def volleyball_matches_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    matches = await get_volleyball_matches(session)
    return {'volleyball_matches': matches}


async def start_volleyball_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])

    match_info = await get_volleyball_match_info_by_id(session, match_id)

    return {'volleyball_match': match_info}


async def volleyball_set_info_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])
    set_number = int(dialog_manager.dialog_data['set_number'])

    full_match_data = await get_current_volleyball_match_info(session, match_id, set_number)

    team_score_data = {'team1_name': full_match_data[0]['team_name'],
                       'team1_score': full_match_data[0]['set_won'],
                       'team2_name': full_match_data[1]['team_name'],
                       'team2_score': full_match_data[1]['set_won'],
                       'tesm1_set_score': full_match_data[0]['set_scores'],
                       'tesm2_set_score': full_match_data[1]['set_scores'],
                       }

    return {'volleyball_match': full_match_data, 'team_score_data': team_score_data, 'set_number': set_number}


async def finish_volleyball_set_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])
    set_number = int(dialog_manager.dialog_data['set_number'])

    full_match_data = await get_current_volleyball_match_info(session, match_id, set_number)

    team_score_data = {'team1_name': full_match_data[0]['team_name'],
                       'team2_name': full_match_data[1]['team_name'],
                       'tesm1_set_score': full_match_data[0]['set_scores'],
                       'tesm2_set_score': full_match_data[1]['set_scores'],
                       }

    return {'volleyball_set': team_score_data, 'set_number': set_number}


async def volleyball_teams_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    sport_id = dialog_manager.start_data['sport_id']

    volleyball_teams = await get_teams_by_sport(sport_id, session)

    return {'teams': [{'name': name, 'id': id_} for name, id_ in volleyball_teams.items()]}


async def volleyball_match_result_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])

    match_full_data = await get_volleyball_match_full_info(session, match_id)

    formated_text = format_volleyball_match_info(match_full_data)

    return {'match_result': formated_text}

async def volleyball_set_group_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    return {'groups': groups_type}