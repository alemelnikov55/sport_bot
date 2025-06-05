from typing import Dict, Any

from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from loader import groups_type
from database.football_requests import get_active_matches, get_match_info_by_id, get_match_teams_optimized
from database.service_requests import get_teams_by_sport, get_team_participants_by_team_and_sport


async def active_matches_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    """Получение списка активных матчей"""
    session = dialog_manager.middleware_data['session']
    matches = await get_active_matches(session)

    return {'matches': matches}


async def start_match_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['match'])

    match_data = await get_match_info_by_id(session, match_id)

    return {'match': match_data}


async def match_info_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data["session"]
    match_id = int(dialog_manager.dialog_data['match'])

    match_team_data = await get_match_teams_optimized(session, match_id)
    match_data = await get_match_info_by_id(session, match_id)

    return {'teams': match_team_data, 'match': match_data}


async def choose_scorer_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session: AsyncSession = dialog_manager.middleware_data["session"]
    team_id = int(dialog_manager.dialog_data['goal_team_id'])
    sport_id = int(dialog_manager.start_data['sport_id'])

    all_participants = await get_team_participants_by_team_and_sport(team_id, sport_id, session)

    return {'participants': [{'name': name.split(' ')[0], 'id': id_} for name, id_ in all_participants.items()]}


async def football_teams_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data['session']
    # sport_identifier = 'football'
    # TODO Ручной ввод
    sport_identifier = 'Мини-футбол'
    
    football_teams = await get_teams_by_sport(sport_identifier, session)

    return {'teams': [{'name': name, 'id': id_} for name, id_ in football_teams.items()]}


async def teams_info_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session = dialog_manager.middleware_data["session"]
    match_id = int(dialog_manager.dialog_data['match'])

    teams = await get_match_teams_optimized(session, match_id)
    return {'teams': teams}


async def choose_faller_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    session: AsyncSession = dialog_manager.middleware_data["session"]
    team_id = int(dialog_manager.dialog_data['red_card_team_id'])
    sport_id = int(dialog_manager.start_data['sport_id'])

    all_participants = await get_team_participants_by_team_and_sport(team_id, sport_id, session)

    return {'players': [{'name': name.split(" ")[0], 'id': id_} for name, id_ in all_participants.items()]}


async def manual_set_group_getter(dialog_manager: DialogManager, **kwargs) -> Dict[str, Any]:
    return {'groups': groups_type}
