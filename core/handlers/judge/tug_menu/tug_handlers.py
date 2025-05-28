import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from database.models import TugStatus
from database.tug_of_war_requests import update_tug_match_status, increment_tug_match_score, create_tug_matches
from handlers.judge.state import TugStates, MainJudgeStates

logger = logging.getLogger(__name__)

logger.level = logging.DEBUG


async def choose_tug_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, pull_id: str):
    dialog_manager.dialog_data['pull_id'] = int(pull_id)

    await dialog_manager.switch_to(TugStates.start_match)
    await call.answer('Выбран матч!')


async def start_tug_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    pull_id = dialog_manager.dialog_data['pull_id']

    await update_tug_match_status(session, pull_id)

    await dialog_manager.switch_to(TugStates.process_match)
    await call.message.reply('Матч начат!')


async def continue_tug_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    pull_id = dialog_manager.dialog_data['pull_id']

    await update_tug_match_status(session, pull_id, TugStatus.IN_PROGRESS)

    await dialog_manager.switch_to(TugStates.process_match)
    await call.message.reply('Матч продолжен!')


async def add_tug_goal_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    session = dialog_manager.middleware_data['session']
    pull_id = dialog_manager.dialog_data['pull_id']
    team_id = int(team_id)

    await increment_tug_match_score(session, pull_id, team_id)

    await dialog_manager.switch_to(TugStates.process_match)
    await call.answer('Добавлен гол!')


async def finish_tug_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(TugStates.confirm_finish_match)
    await call.answer('Подтвердите завершение матча!')


async def confirm_finish_tug_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    pull_id = dialog_manager.dialog_data['pull_id']

    await update_tug_match_status(session, pull_id, TugStatus.FINISHED)

    await dialog_manager.switch_to(TugStates.match)
    await call.answer('Подтвердите завершение матча!')


async def first_tug_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['tug_manual_team1'] = int(team_id)

    await dialog_manager.next()
    await call.answer()


async def second_tug_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['tug_manual_team2'] = int(team_id)

    await dialog_manager.switch_to(TugStates.set_group)
    await call.answer('Выберите группу')


async def tug_set_group_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, group_type: str):
    session = dialog_manager.middleware_data['session']
    team1_id = dialog_manager.dialog_data['tug_manual_team1']
    team2_id = dialog_manager.dialog_data['tug_manual_team2']
    data_to_create = {group_type: [(team1_id, team2_id)]}

    await create_tug_matches(session, data_to_create)

    await dialog_manager.switch_to(TugStates.match)
    await call.answer('Матч создан!')


async def manual_tug_match_add_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(TugStates.manual_match_create_1)
    await call.answer('Выберите команду')


async def back_tug_choose_match(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)
    await call.answer('Назад!')


async def back_finish_tug_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(TugStates.process_match)
    await call.message.answer('Назад!')


async def back_tug_choose_team_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(TugStates.match, data=dialog_manager.start_data)
    await call.answer('Назад!')
