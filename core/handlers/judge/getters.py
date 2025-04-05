from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import get_active_matches, get_match_info_by_id, get_match_teams_info, \
    get_match_teams_optimized
from database.service_requests import get_all_sports, get_teams_by_sport, get_team_participants_by_sport


async def get_sports(dialog_manager: DialogManager, **kwargs):
    """Получение списка видов сопорта"""
    sports = await get_all_sports()
    return {'sports': [{'name': name, 'id': id_} for name, id_ in sports.items()]}


async def active_matches_getter(dialog_manager: DialogManager, **kwargs):
    """Получение списка активных матчей"""
    matches = await get_active_matches()
    return {'matches': matches}


async def start_match_getter(dialog_manager: DialogManager, **kwargs):
    match_id = int(dialog_manager.dialog_data['match'])

    match_data = await get_match_info_by_id(match_id)

    return {'match': match_data}


async def match_info_getter(dialog_manager: DialogManager, **kwargs):
    match_id = int(dialog_manager.dialog_data['match'])

    match_team_data = await get_match_teams_optimized(match_id)
    match_data = await get_match_info_by_id(match_id)
    print(match_team_data)
    return {'teams': match_team_data, 'match': match_data}


async def choose_scorer_getter(dialog_manager: DialogManager, **kwargs):
    session: AsyncSession = dialog_manager.middleware_data["session"]
    team_id = int(dialog_manager.dialog_data['goal_team_id'])
    sport_id = int(dialog_manager.dialog_data['sport'])
    print(f'team_id: {team_id}')
    print(f'sport_id: {sport_id}')
    all_participants = await get_team_participants_by_sport(team_id, sport_id, session)

    return {'participants': [{'name': name.split(' ')[0], 'id': id_} for name, id_ in all_participants.items()]}
