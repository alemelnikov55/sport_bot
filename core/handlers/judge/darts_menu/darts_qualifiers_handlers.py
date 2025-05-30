from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from database.darts_requests import add_darts_qualifiers_result
from handlers.judge.state import MainJudgeStates, DartsStates


async def darts_team_choose_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['darts_team_id'] = int(team_id)

    await dialog_manager.next()
    await call.answer('Команда выбрана')


async def darts_player_choose_qualifiers_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager,
                                                 player_id: str):
    player_id = int(player_id)
    dialog_manager.dialog_data['darts_player_id'] = player_id

    await dialog_manager.next()
    await call.answer('Игрок выбран')


async def darts_score_input_qualifiers_handler(message: Message, message_inpout: MessageInput, dialog_manager: DialogManager):
    try:
        score = int(message.text.strip())
    except ValueError:
        await message.answer('В результате должны быть только цифры, попробуйте еще раз')
        return

    dialog_manager.dialog_data['darts_scores'] = score

    await dialog_manager.next()


async def darts_confirm_result_qualifiers_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    player_id = dialog_manager.dialog_data['darts_player_id']
    team_id = dialog_manager.dialog_data['darts_team_id']
    score = dialog_manager.dialog_data['darts_scores']
    telegram_id = dialog_manager.start_data['judge_telegram_id']

    await add_darts_qualifiers_result(session, player_id, team_id, score, telegram_id)

    await call.answer('Результат сохранен!')
    await dialog_manager.switch_to(DartsStates.choose_team)


async def history_darts_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(DartsStates.inpout_history)
    await call.answer('История!')


async def darts_playoff_start_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(DartsStates.playoff_choose_first_player)
    await call.answer('Выбор первого игрока')


async def back_darts_to_choose_team_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)
    await call.answer('Назад!')


async def back_to_choose_team_darts_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(DartsStates.choose_team, data=dialog_manager.start_data)
    await call.answer('Назад!')
