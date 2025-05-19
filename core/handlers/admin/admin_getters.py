from aiogram_dialog import DialogManager

from database.football_requests import get_football_matches_for_team, get_team_goals_in_match, get_match_info_by_id
from database.service_requests import get_teams_by_sport, get_participants_by_sport
from handlers.judge.football_menu.football_getters import football_teams_getter


def get_team_name_from_match(match: dict, team_id: int) -> str:
    if match["team1_id"] == team_id:
        return match["team1_name"]
    elif match["team2_id"] == team_id:
        return match["team2_name"]


async def football_matches_getter(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    team_id = int(dialog_manager.dialog_data['team_to_fix'])

    raw_data = await get_football_matches_for_team(session, team_id)

    formated_data = [{'button_text': f'{data["team1"]["name"]} - {data["team2"]["name"]} {"☑️" if data["status"] == "FINISHED" else "🟢"}', 'match_id': data['match_id']} for data in raw_data]

    return {'matches': formated_data}


async def football_goal_getter(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    team_id = int(dialog_manager.dialog_data['team_to_fix'])
    match_id = int(dialog_manager.dialog_data['match_to_fix'])

    raw_goals = await get_team_goals_in_match(session, match_id, team_id)

    goals = [{'scorer': f'{goal["scorer_name"]}_{goal["scorer_id"]}', 'id': goal['goal_id']} for goal in raw_goals]
    return {'goals': goals}


async def admin_fix_goal_approve_getter(dialog_manager: DialogManager, **kwargs):
    # session = dialog_manager.middleware_data['session']
    team_id = int(dialog_manager.dialog_data['team_to_fix'])
    match_id = int(dialog_manager.dialog_data['match_to_fix'])

    raw_data = await get_match_info_by_id(match_id)

    team_name = get_team_name_from_match(raw_data, team_id)
    march_name = f'{raw_data["team1_name"]} - {raw_data["team2_name"]}'

    return {'team_name': team_name, 'march_name': march_name}


async def create_groups_tournament_football_getter(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    sport_name = dialog_manager.dialog_data['sport_name']

    teams = await get_teams_by_sport(sport_name, session)

    teams_amount = len(teams)
    dialog_manager.dialog_data['teams_count'] = teams_amount
    dialog_manager.dialog_data['teams_for_groups'] = teams

    return {'teams_count': teams_amount}


async def create_groups_tournament_volleyball_getter(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']
    sport_name = dialog_manager.dialog_data['sport_name']

    teams = await get_teams_by_sport(sport_name, session)

    teams_amount = len(teams)
    dialog_manager.dialog_data['teams_count'] = teams_amount
    dialog_manager.dialog_data['teams_for_groups'] = teams

    return {'teams_count': teams_amount}


async def create_groups_tournament_pong_getter(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']

    players_id = await get_participants_by_sport(session, 'pong')

    teams_amount = len(players_id)
    dialog_manager.dialog_data['player_count'] = teams_amount
    dialog_manager.dialog_data['player_for_groups'] = players_id

    return {'players_count': teams_amount}


async def create_groups_tournament_tug_getter(dialog_manager: DialogManager, **kwargs):
    session = dialog_manager.middleware_data['session']

    # players_id = await get_teams_by_sport('tug_of_war', session)
    sport_name = dialog_manager.dialog_data['sport_name']

    teams = await get_teams_by_sport(sport_name, session)

    # teams_amount = len(players_id)
    teams_amount = len(teams)
    dialog_manager.dialog_data['tug_teams_count'] = teams_amount
    # dialog_manager.dialog_data['tug_teams_for_groups'] = players_id
    dialog_manager.dialog_data['tug_teams_for_groups'] = teams

    return {'tug_team_count': teams_amount}
