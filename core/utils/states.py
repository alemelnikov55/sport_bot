from aiogram.fsm.state import StatesGroup, State


class GroupCreationStates(StatesGroup):
    get_teams_amount = State()