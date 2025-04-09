from aiogram.fsm.state import StatesGroup, State


class MainJudgeStates(StatesGroup):
    sport = State()


class FootballStates(StatesGroup):
    match = State()
    start_match = State()
    goal = State()
    choose_scorer = State()

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
