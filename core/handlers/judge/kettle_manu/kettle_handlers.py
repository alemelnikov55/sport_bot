import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from database.kettle_requests import save_kettle_results
from database.service_requests import get_participants_by_id
from handlers.judge.state import MainJudgeStates, KettleStates

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def kettle_team_choose_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['kettle_team_id'] = int(team_id)

    await dialog_manager.next()
    await call.answer('Команда выбрана')


async def kettle_choose_lifter_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, lifter_id: str):
    lifter_id = int(lifter_id)
    session = dialog_manager.middleware_data['session']
    lifter = await get_participants_by_id(session, lifter_id)

    name, age, gender = lifter.full_name, lifter.age, lifter.gender

    dialog_manager.dialog_data['kettle_lifter'] = {'name': name, 'age': age, 'gender': gender, 'id': lifter_id}

    logger.warning(dialog_manager.dialog_data['kettle_lifter'])

    await dialog_manager.next()
    await call.answer('Спортсмен выбран')


async def kettle_choose_category_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, category: str):
    dialog_manager.dialog_data['kettle_category'] = category
    await dialog_manager.switch_to(KettleStates.get_lift_count)
    await call.answer('Назад!')
    logger.debug(dialog_manager.dialog_data)


async def lifter_result_handler(message: Message, message_inpout: MessageInput, dialog_manager: DialogManager):
    try:
        lift_count = int(message.text.strip())
    except ValueError:
        await message.answer('В числе поднятий должны быть только цифры, попробуйте еще раз')
        return

    dialog_manager.dialog_data['lift_count'] = lift_count
    await dialog_manager.next()


async def lifter_weight_handler(message: Message, message_inpout: MessageInput, dialog_manager: DialogManager):
    try:
        lifter_weight = int(message.text.strip())
    except ValueError:
        await message.answer('В числе поднятий должны быть только цифры, попробуйте еще раз')
        return

    dialog_manager.dialog_data['lifter_weight'] = lifter_weight
    await dialog_manager.next()


async def kettle_confirm_result_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    lifter_id = dialog_manager.dialog_data.pop('kettle_lifter')['id']
    lift_count = dialog_manager.dialog_data.pop('lift_count')
    telegram_id = call.message.chat.id
    weight = dialog_manager.dialog_data.pop('lifter_weight')

    await save_kettle_results(session, lifter_id, lift_count, telegram_id, weight)

    del dialog_manager.dialog_data['kettle_team_id']

    await dialog_manager.switch_to(KettleStates.choose_team)
    await call.answer('Запись сохранена!')


async def history_kettle_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(KettleStates.inpout_history)
    await call.answer('Вывод результатов')


async def back_kettle_team_choose_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)
    await call.answer('Назад!')


# async def back_kettle_choose_lifter_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     await dialog_manager.switch_to(KettleStates.choose_team)
#     await call.answer('Назад!')
#
#
# async def back_kettle_count(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     await dialog_manager.switch_to(KettleStates.choose_team)
#     await call.answer('Назад!')
#
#
# async def back_kettle_history_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     await dialog_manager.switch_to(KettleStates.choose_team)
#     await call.answer('Назад!')
#
#
# async def cancel_kettle_confirm_result(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     await dialog_manager.switch_to(KettleStates.choose_team)
#     await call.answer('Запись отменена')


async def back_to_choose_team(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(KettleStates.choose_team)
    await call.answer('Назад!')