from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import change_match_status, add_goal
from database.models import MatchStatus, async_session
from handlers.judge.state import FootballStates, MainJudgeStates


async def choose_match_back_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """обработчик кнопки назад в меню выбора матча"""
    await dialog_manager.start(MainJudgeStates.sport)


async def choose_sport_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, sport_id: int):
    """Обработчик выбора видов спорта"""
    # dialog_manager.dialog_data['sport'] = sport_id
    await call.answer('Выбран спорт!')
    # await dialog_manager.switch_to(FootballStates.match)
    await dialog_manager.start(FootballStates.match)


async def choose_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, match_id: int):
    dialog_manager.dialog_data['match'] = match_id
    dialog_manager.dialog_data['sport'] = 5
    print(dialog_manager.dialog_data)
    await call.answer('Выбран матч!')
    await dialog_manager.next()


async def start_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    match_id = int(dialog_manager.dialog_data['match'])
    async with async_session() as session:
        await change_match_status(match_id, MatchStatus.IN_PROGRESS, session)
        await session.commit()
    await dialog_manager.next()


async def add_goal_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: int):
    dialog_manager.dialog_data['goal_team_id'] = team_id
    print(dialog_manager.dialog_data)
    await dialog_manager.next()


async def finish_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def choose_scorer_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, scorer_id: str):
    match_id = int(dialog_manager.dialog_data['match'])
    await add_goal(match_id, int(scorer_id))
    await dialog_manager.switch_to(FootballStates.goal)



