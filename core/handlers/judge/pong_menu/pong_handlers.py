import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from database.models.pong_models import PongMatchStatus
from database.pong_requests import get_pong_next_available_set, update_pong_match_status, update_pong_set_status, \
    increment_pong_set_score, create_pong_matches
from handlers.judge.state import PongStates, MainJudgeStates

logger = logging.getLogger(__name__)


async def select_pong_match(call: CallbackQuery, button: Button, dialog_manager: DialogManager, match_id: str):
    dialog_manager.dialog_data['pong_match_id'] = match_id
    dialog_manager.dialog_data['sport'] = 'pong'
    await call.answer('Выбран матч!')
    await dialog_manager.next()


async def pong_manual_match_add_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(PongStates.manual_match_create_team_1)


async def start_pong_matches_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])
    logger.info(f'match_id = {match_id}')
    set_info = await get_pong_next_available_set(session, match_id)
    set_num = set_info.set_number

    dialog_manager.dialog_data['pong_set_number'] = set_num

    logger.info(f'{dialog_manager.dialog_data}')

    await update_pong_match_status(session, match_id, PongMatchStatus.IN_PROGRESS)

    update_info = await update_pong_set_status(session, match_id, set_num, PongMatchStatus.IN_PROGRESS)
    set_id = update_info.set_id
    dialog_manager.dialog_data['pong_set_id'] = set_id

    await dialog_manager.next()
    await call.answer('Начат матч!')


async def add_pong_goal_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, player_id: str):
    session = dialog_manager.middleware_data['session']
    current_set_id = int(dialog_manager.dialog_data['pong_set_id'])
    player_id = int(player_id)

    await increment_pong_set_score(session, current_set_id, player_id)
    await dialog_manager.switch_to(PongStates.process_set)
    await call.answer('Гол добавлен!')


async def continue_pong_matches_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])

    actual_set_info = await get_pong_next_available_set(session, match_id)
    logger.info(f'dialog_manager.dialog_data {dialog_manager.dialog_data}')
    dialog_manager.dialog_data['pong_set_number'] = actual_set_info.set_number
    dialog_manager.dialog_data['pong_set_id'] = actual_set_info.set_id

    await dialog_manager.switch_to(PongStates.process_set)
    await call.answer('Продолжен матч!')


async def confirm_pong_finish_set_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])
    old_set_num = int(dialog_manager.dialog_data['pong_set_number'])

    await update_pong_set_status(session, match_id, old_set_num, PongMatchStatus.FINISHED)

    new_set = await get_pong_next_available_set(session, match_id)
    new_set_id = new_set.set_id
    new_set_number = new_set.set_number

    dialog_manager.dialog_data['pong_set_number'] = new_set_number
    dialog_manager.dialog_data['pong_set_id'] = new_set_id

    await update_pong_set_status(session, match_id, new_set_number, PongMatchStatus.IN_PROGRESS)

    await call.answer('Сет завершен!')
    await dialog_manager.switch_to(PongStates.process_set, ShowMode.EDIT)


async def confirm_finish_pong_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['pong_match_id'])
    set_num = int(dialog_manager.dialog_data['pong_set_number'])

    await update_pong_set_status(session, match_id, set_num, PongMatchStatus.FINISHED)
    await update_pong_match_status(session, match_id, PongMatchStatus.FINISHED)

    await dialog_manager.switch_to(PongStates.match)
    await call.answer('Матч завершен!')


async def finish_pong_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(PongStates.finish_match)
    await call.answer('Подтвердите завершение матча')


async def finish_pong_set_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(PongStates.finish_set)
    await call.answer('Подтвердите завершение сета')


async def first_pong_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['pong_manual_team1_id'] = team_id
    await dialog_manager.switch_to(PongStates.manual_match_create_player_1)


async def pong_player_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, player_id: str):
    if dialog_manager.dialog_data.get('pong_manual_player1_id'):
        player1_id = int(dialog_manager.dialog_data['pong_manual_player1_id'])
        player2_id = int(player_id)
        session = dialog_manager.middleware_data['session']
        match_info = {'': [(player1_id, player2_id)]}
        await create_pong_matches(session, match_info)
        await dialog_manager.switch_to(PongStates.match)
        await call.answer('Матч создан!')
        return

    dialog_manager.dialog_data['pong_manual_player1_id'] = player_id
    del dialog_manager.dialog_data['pong_manual_team1_id']

    await dialog_manager.switch_to(PongStates.manual_match_create_team_1)


async def back_pong_matches_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)
    await call.answer('Назад!')


async def back_pong_start_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()
    await call.answer('Назад!')


async def back_pong_progress_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(PongStates.match)
    await call.answer('Назад!')


async def back_pong_finish_set_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(PongStates.process_set)
    await call.answer('Назад!')


async def back_pong_finish_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(PongStates.process_set)
    await call.answer('Назад!')


async def back_pong_manual_add_match(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    try:
        del dialog_manager.dialog_data['pong_manual_team1_id']
    except KeyError:
        pass
    await dialog_manager.switch_to(PongStates.match)