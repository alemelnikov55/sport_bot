from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from api_requests.api_base_config import api
from api_requests.data_preparation_fonc import VolleyballResultBuilder
from database.models import VolleyballMatchStatus
from database.volleyball_requests import update_volleyball_set_status, update_volleyball_match_status, \
    increment_volleyball_set_score, create_volleyball_matches, get_next_available_set
from handlers.judge.state import VolleyballStates, MainJudgeStates


async def choose_volleyball_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, match_id: int):
    """Обработчик выбора матча в волейболе"""
    dialog_manager.dialog_data['volleyball_match'] = match_id
    dialog_manager.dialog_data['sport'] = 'volleyball'
    await call.answer('Выбран матч!')
    await dialog_manager.next()


async def start_volleyball_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Обработчик подтверждения начала волейбольного матча"""
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])

    set_info = await get_next_available_set(session, match_id)
    set_num = set_info.set_number

    dialog_manager.dialog_data['set_number'] = set_num

    await update_volleyball_match_status(session, match_id, VolleyballMatchStatus.IN_PROGRESS)

    update_info = await update_volleyball_set_status(session, match_id, set_num, VolleyballMatchStatus.IN_PROGRESS)
    set_id = update_info.set_id
    dialog_manager.dialog_data['volleyball_set_id'] = set_id

    await dialog_manager.next()
    await call.answer('Матч начат!')


async def add_volleyball_goal_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: int):
    session = dialog_manager.middleware_data['session']
    current_set_id = int(dialog_manager.dialog_data['volleyball_set_id'])
    team_id = int(team_id)

    await increment_volleyball_set_score(session, current_set_id, team_id)
    await dialog_manager.switch_to(VolleyballStates.process_set)
    await call.answer('Гол добавлен!')


async def finish_volleyball_set_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(VolleyballStates.finish_set)
    await call.answer('Подтвердите завершение сета')


async def confirm_finish_volleyball_set_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])
    old_set_num = int(dialog_manager.dialog_data['set_number'])

    await update_volleyball_set_status(session, match_id, old_set_num, VolleyballMatchStatus.FINISHED)

    new_set = await get_next_available_set(session, match_id)
    new_set_id = new_set.set_id
    new_set_number = new_set.set_number

    dialog_manager.dialog_data['set_number'] = new_set_number
    dialog_manager.dialog_data['volleyball_set_id'] = new_set_id

    await update_volleyball_set_status(session, match_id, new_set_number, VolleyballMatchStatus.IN_PROGRESS)

    builder = VolleyballResultBuilder(session)
    goal_info = await builder.build_for_match(match_id)
    api.send_results(goal_info)

    await call.answer('Сет завершен!')
    await dialog_manager.switch_to(VolleyballStates.process_set, ShowMode.EDIT)


async def finish_volleyball_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(VolleyballStates.finish_match)


async def confirm_finish_volleyball_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])
    set_num = int(dialog_manager.dialog_data['set_number'])

    await update_volleyball_set_status(session, match_id, set_num, VolleyballMatchStatus.FINISHED)
    await update_volleyball_match_status(session, match_id, VolleyballMatchStatus.FINISHED)

    builder = VolleyballResultBuilder(session)
    goal_info = await builder.build_for_match(match_id)
    api.send_results(goal_info)

    await dialog_manager.switch_to(VolleyballStates.match)
    await call.answer('Матч завершен!')


async def manual_volleyball_match_add_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(VolleyballStates.manual_match_create_1)


async def first_volleyball_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['volleyball_manual_team1'] = team_id
    await call.answer()
    await dialog_manager.next()


async def second_volleyball_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['volleyball_manual_team2'] = int(team_id)

    await dialog_manager.switch_to(VolleyballStates.manual_set_group)
    await call.answer('Выберите группу')


async def volleyball_set_group_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, group_type: str):
    session = dialog_manager.middleware_data['session']
    team2_id = int(dialog_manager.dialog_data['volleyball_manual_team2'])
    team1_id = int(dialog_manager.dialog_data['volleyball_manual_team1'])
    data_to_create = {group_type: [(team1_id, team2_id)]}

    await create_volleyball_matches(session, data_to_create)

    await dialog_manager.switch_to(VolleyballStates.match)
    await call.answer('Матч создан!')


async def continue_volleyball_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['volleyball_match'])

    actual_set_info = await get_next_available_set(session, match_id)

    dialog_manager.dialog_data['set_number'] = actual_set_info.set_number
    dialog_manager.dialog_data['volleyball_set_id'] = actual_set_info.set_id

    await dialog_manager.switch_to(VolleyballStates.process_set)


async def back_choose_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)


async def back_volleyball_finish_set_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(VolleyballStates.process_set)


async def back_volleyball_finish_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(VolleyballStates.process_set)


async def back_volleyball_to_choose_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(VolleyballStates.match, data=dialog_manager.start_data)
    await call.answer('Назад!')
