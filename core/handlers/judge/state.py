from aiogram.fsm.state import StatesGroup, State


class MainJudgeStates(StatesGroup):
    sport = State()


class FootballStates(StatesGroup):
    match = State()
    start_match = State()
    process_match = State()
    choose_scorer = State()

    red_card_choose_team = State()
    red_card_choose_player = State()

    confirm_finish_match = State()

    manual_match_create_1 = State()
    manual_match_create_2 = State()

    manual_scorer_add = State()


class VolleyballStates(StatesGroup):
    match = State()
    start_match = State()
    set = State()
    process_set = State()

    finish_set = State()
    finish_match = State()

    confirm_finish_match = State()
    manual_match_create_1 = State()
    manual_match_create_2 = State()


class AdminStates(StatesGroup):
    start_menu = State()
    choose_sport_to_fix = State()
    football_choose_team_to_fix = State()
    football_choose_match_to_fix = State()
    football_choose_goal_to_fix = State()
    football_fix_goal_approve = State()

    create_groups = State()
    create_football_tournament_groups = State()
    create_volleyball_tournament_groups = State()

    add_judge = State()

