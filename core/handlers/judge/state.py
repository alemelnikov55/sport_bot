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
    manual_set_group = State()

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
    manual_set_group = State()


class PongStates(StatesGroup):
    match = State()
    start_match = State()
    set = State()
    process_set = State()

    finish_set = State()
    finish_match = State()

    confirm_finish_match = State()
    manual_match_create_1 = State()
    manual_match_create_team_1 = State()
    manual_match_create_player_1 = State()
    manual_match_create_2 = State()
    pong_set_group = State()


class RunStates(StatesGroup):
    get_runner_number = State()
    get_runner_time = State()
    confirm_runner_time = State()
    last_runners = State()

    inpout_history = State()


class RelayStates(StatesGroup):
    choose_team = State()
    get_team_time = State()
    conform_team_time = State()

    inpout_history = State()


class TugStates(StatesGroup):
    match = State()
    start_match = State()
    process_match = State()
    choose_winner = State()

    confirm_finish_match = State()

    manual_match_create_1 = State()
    manual_match_create_2 = State()
    set_group = State()


class KettleStates(StatesGroup):
    choose_team = State()
    chose_lifter = State()
    get_weight = State()
    get_lift_count = State()
    confirm_lift_count = State()

    inpout_history = State()

class DartsStates(StatesGroup):
    choose_team = State()
    choose_player = State()
    get_score = State()
    confirm_score = State()

    match_list = State()

    playoff_choose_first_player = State()
    playoff_choose_second_player = State()
    playoff_choose_type = State()
    playoff_confirm_start_match = State()
    playoff_process_match = State()

    inpout_history = State()


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
    create_pong_tournament_groups = State()
    choose_gender_pong = State()
    create_tug_tournament_groups = State()

    send_result = State()

    add_judge = State()

