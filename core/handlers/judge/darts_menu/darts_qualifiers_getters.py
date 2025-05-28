import logging
from typing import Dict, Any

from aiogram_dialog import DialogManager

from database.darts_requests import get_darts_judge_history
from database.service_requests import get_teams_by_sport, get_team_participants_by_team_and_sport, \
    get_participants_by_id

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def darts_team_choose_qualifiers_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    sport = int(dialog_manager.start_data['sport_id'])

    teams = await get_teams_by_sport(sport, session)

    return {'darts_teams': [{'name': name, 'id': id_} for name, id_ in teams.items()]}


async def darts_player_choose_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    team_id = dialog_manager.dialog_data['darts_team_id']
    sport_id = int(dialog_manager.start_data['sport_id'])

    players = await get_team_participants_by_team_and_sport(team_id, sport_id, session)

    return {'players': [{'name': f'{name.split(" ")[0]} {id_}', 'id': id_} for name, id_ in players.items()]}


async def darts_confirm_result_qualifiers_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    player_id = dialog_manager.dialog_data['darts_player_id']
    score = dialog_manager.dialog_data['darts_scores']
    player = await get_participants_by_id(session, player_id)
    name = player.full_name

    return {'player_name': name, 'darts_scores': score}


async def darts_history_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    telegram_id = dialog_manager.start_data['judge_telegram_id']

    history_results = await get_darts_judge_history(session, telegram_id)

    printable_results = '\n'.join(
        [f'Игрок <b>{result['short_name']}</b>: {result['scores']} очков' for result in history_results]
    )

    return {'history': printable_results}
