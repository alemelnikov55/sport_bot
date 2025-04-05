from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import change_match_status, add_goal, create_match
from database.models import MatchStatus, async_session
from database.service_requests import get_teams_by_sport
from handlers.judge.state import FootballStates, MainJudgeStates


async def choose_match_back_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Обработчик кнопки назад в меню выбора матча"""
    await dialog_manager.start(MainJudgeStates.sport)


async def choose_sport_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, sport_id: str):
    """Обработчик выбора видов спорта"""
    await call.answer('Выбран спорт!')
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


async def add_goal_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['goal_team_id'] = team_id
    print(dialog_manager.dialog_data)
    await dialog_manager.next()


async def choose_scorer_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, scorer_id: str):
    match_id = int(dialog_manager.dialog_data['match'])
    await add_goal(match_id, int(scorer_id))
    await dialog_manager.switch_to(FootballStates.goal)


async def finish_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FootballStates.confirm_finish_match)
    await call.answer('Подтвердите завершение матча!')


async def confirm_finish_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Завершение матча"""
    session = dialog_manager.middleware_data['session']
    await call.answer('Матч завершен!')
    match_id = int(dialog_manager.dialog_data['match'])
    await change_match_status(match_id, MatchStatus.FINISHED, session)
    await dialog_manager.switch_to(FootballStates.match)


async def manual_football_match_add_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Обработчик добавления матча вручную"""
    await dialog_manager.switch_to(FootballStates.manual_match_create_1)


async def first_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['manual_team1'] = team_id
    await call.answer(f'Выбрана команда {team_id}')
    await dialog_manager.next()


async def second_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    second_team = int(team_id)
    first_team = int(dialog_manager.dialog_data['manual_team1'])

    await create_match(first_team, second_team)

    await dialog_manager.switch_to(FootballStates.match)
    await call.answer(f'Выбрана команда {team_id}')
