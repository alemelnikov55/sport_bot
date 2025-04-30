import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from database.run_requests import save_running_result
from database.service_requests import get_participants_by_id
from handlers.judge.state import MainJudgeStates, RunStates, KettleStates

logger = logging.getLogger(__name__)


# async def kettle_number_handler(message: Message, message_inpout: MessageInput,
#                                 dialog_manager: DialogManager):
#     try:
#         lifter_id = int(message.text.strip())
#     except ValueError:
#         await message.answer('В номере должны быть только цифры, попробуйте еще раз')
#         return
#
#     session = dialog_manager.middleware_data['session']
#     runner = await get_participants_by_id(session, lifter_id)
#
#     if runner is None:
#         await message.answer('Такого спортсмена нет, попробуйте еще раз')
#         return
#
#     dialog_manager.dialog_data['lifter_id'] = runner.participant_id
#     dialog_manager.dialog_data['lifter_name'] = runner.short_name
#
#     await dialog_manager.switch_to(KettleStates.get_lift_count)

async def kettle_team_choose_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['kettle_team_id'] = int(team_id)

    await dialog_manager.next()
    await call.answer('Команда выбрана')


async def kettle_choose_lifter_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, lifter_id: str):
    dialog_manager.dialog_data['kettle_lifter_id'] = int(lifter_id)
    await dialog_manager.switch_to(KettleStates.get_lift_count)
    await call.answer('Спортсмен выбран')


async def history_kettle_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(KettleStates.inpout_history)
    await call.answer('Назад!')


async def back_kettle_team_choose_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)
    await call.answer('Назад!')


async def back_kettle_choose_lifter_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(KettleStates.choose_team)
    await call.answer('Назад!')
