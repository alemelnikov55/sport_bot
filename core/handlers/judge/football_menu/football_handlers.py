from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from api_requests.api_base_config import api
from api_requests.data_preparation_fonc import FootballResultBuilder
from database.football_requests import change_match_status, add_goal, create_match, add_faller
from database.models import MatchStatus, async_session
from handlers.judge.state import FootballStates, MainJudgeStates


async def choose_match_back_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    """Обработчик кнопки назад в меню выбора матча"""
    await dialog_manager.start(MainJudgeStates.sport)


async def choose_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, match_id: int):
    dialog_manager.dialog_data['match'] = match_id
    dialog_manager.dialog_data['sport'] = 5
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
    await dialog_manager.next()


async def choose_scorer_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, scorer_id: str):
    session = dialog_manager.middleware_data['session']
    match_id = int(dialog_manager.dialog_data['match'])

    builder = FootballResultBuilder(session)
    goal_data = await builder.build_for_match(match_id)
    api.send_results(goal_data)

    await add_goal(match_id, int(scorer_id))
    await dialog_manager.switch_to(FootballStates.process_match)
    await call.answer('Гол добавлен!')


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
    dialog_manager.dialog_data['manual_team2'] = int(team_id)

    await dialog_manager.switch_to(FootballStates.manual_set_group)
    await call.answer(f'Выбрана команда {team_id}')


async def manual_set_group_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, group_type: str):
    session = dialog_manager.middleware_data['session']
    first_team = int(dialog_manager.dialog_data['manual_team1'])
    second_team = int(dialog_manager.dialog_data['manual_team2'])

    await create_match(session, first_team, second_team, group_type)

    await dialog_manager.switch_to(FootballStates.match)
    await call.answer('Поехали!')


async def back_choose_scorer_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FootballStates.process_match)
    await call.answer('Меню матча')


async def back_finish_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FootballStates.process_match)
    await call.answer('Меню матчей')


async def back_football_to_choose_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(FootballStates.match, data=dialog_manager.start_data)
    await call.answer('Назад')


async def red_card_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FootballStates.red_card_choose_team)


async def red_card_team_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['red_card_team_id'] = team_id
    await dialog_manager.switch_to(FootballStates.red_card_choose_player)


async def red_card_player_select_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, player_id: str):
    session = dialog_manager.middleware_data['session']
    player_id = int(player_id)
    match_id = int(dialog_manager.dialog_data['match'])

    await add_faller(session, player_id, match_id)

    await dialog_manager.switch_to(FootballStates.process_match)
    await call.answer('Карточка выдана!')


async def add_manual_scorer_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(FootballStates.manual_scorer_add)
    await call.answer('Выберите игрока')


async def manual_scorer_inpout_handler(message: Message, message_input: MessageInput, dialog_manager: DialogManager,):
    text = message.text
    session = dialog_manager.middleware_data['session']

    if not text.isdigit():
        await message.reply('Номер игрока должен быть числом')
        return

    scorer_id = int(text)
    match_id = int(dialog_manager.dialog_data['match'])

    await add_goal(match_id, scorer_id)

    builder = FootballResultBuilder(session)
    goal_data = await builder.build_for_match(match_id)
    api.send_results(goal_data)

    await dialog_manager.switch_to(FootballStates.process_match)
