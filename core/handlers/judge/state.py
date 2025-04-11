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
