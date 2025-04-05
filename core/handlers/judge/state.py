from aiogram.fsm.state import StatesGroup, State


class FootballStates(StatesGroup):
    sport = State()
    match = State()
    start_match = State()
    goal = State()
    choose_scorer = State()

    confirm_finish_match = State()
    manual_match_create_1 = State()
    manual_match_create_2 = State()


class MainJudgeStates(StatesGroup):
    sport = State()
