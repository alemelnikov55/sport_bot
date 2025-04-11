from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select

from database.football_requests import delete_goal
from handlers.judge.state import AdminStates

SPORTS = {'football': AdminStates.football_choose_team_to_fix}


async def fix_score_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.choose_sport_to_fix)
    await call.answer('Корректировка счета')


async def choose_sport_to_fix_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, sport_id: str):
    dialog_manager.dialog_data['sport_to_fix'] = sport_id
    await dialog_manager.switch_to(SPORTS[sport_id])
    await call.answer('Выбран спорт')


async def choose_team_to_fix_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['team_to_fix'] = team_id
    await dialog_manager.next()


async def choose_match_to_fix_handler(call: CallbackQuery, button: Select, dialog_manager: DialogManager, match_id: str):
    dialog_manager.dialog_data['match_to_fix'] = match_id
    await dialog_manager.switch_to(AdminStates.football_choose_goal_to_fix)
    await call.answer('Выбран матч')


async def choose_goal_to_fix_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, goal_id: str):
    dialog_manager.dialog_data['goal_to_fix'] = goal_id
    await dialog_manager.next()
    await call.answer('Выбран гол')


async def admin_fix_goal_approve_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    goal_id = int(dialog_manager.dialog_data['goal_to_fix'])
    team_id = int(dialog_manager.dialog_data['team_to_fix'])
    match_id = int(dialog_manager.dialog_data['match_to_fix'])

    await delete_goal(session, match_id, goal_id, team_id)

    await dialog_manager.switch_to(AdminStates.start_menu)
    await call.answer('Гол удален')


async def admin_fix_goal_refuse_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.start_menu)
    await call.answer('Отмена удаления')


async def back_admin_choose_goal_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def back_admin_choose_match_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def back_admin_choose_team_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def back_admin_choose_sport_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()
