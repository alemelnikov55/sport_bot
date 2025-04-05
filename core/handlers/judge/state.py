from aiogram.fsm.state import StatesGroup, State


class FootballStates(StatesGroup):
    sport = State()
    match = State()
    start_match = State()
    goal = State()
    choose_scorer = State()
    finish_match = State()


class MainJudgeStates(StatesGroup):
    sport = State()
