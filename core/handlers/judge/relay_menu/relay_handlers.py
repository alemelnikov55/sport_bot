import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from database.relay_requests import save_relay_result
from handlers.judge.run_menu.run_handlers import parse_time_to_seconds
from handlers.judge.state import MainJudgeStates, RelayStates

logger = logging.getLogger(__name__)


async def relay_team_choose_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    logger.debug(dialog_manager.dialog_data)
    dialog_manager.dialog_data['relay_team_id'] = int(team_id)

    await dialog_manager.next()
    await call.answer('Команда выбрана')


async def relay_result_handler(message: Message, message_inpout: MessageInput,
                               dialog_manager: DialogManager):
    raw_time = message.text.strip()
    dialog_manager.dialog_data['relay_time'] = parse_time_to_seconds(raw_time)

    await dialog_manager.switch_to(RelayStates.conform_team_time)


async def relay_confirm_result_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    team_id = dialog_manager.dialog_data['relay_team_id']
    time = dialog_manager.dialog_data['relay_time']
    judge_id = call.message.chat.id

    await save_relay_result(session, team_id, time, judge_id)

    await dialog_manager.switch_to(RelayStates.choose_team)
    await call.answer('Запись сохранена!')


async def history_relay_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RelayStates.inpout_history)


async def back_relay_team_choose_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)
    await call.answer('Назад!')


async def back_relay_time_register_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RelayStates.choose_team)
    await call.answer('Назад!')


async def back_relay_history_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RelayStates.choose_team)
    await call.answer('Назад!')


async def cancel_relay_confirm_result_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RelayStates.choose_team)
    await call.answer('Отмена')
