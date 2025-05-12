import logging
from pprint import pprint

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from database.darts_requests import create_darts_playoff_match, increment_player_win, update_playoff_winner
from database.models import DartsPlayoffType
from handlers.judge.state import DartsStates

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def darts_playoff_get_match_list_handler(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(DartsStates.match_list)
    await callback.answer('Выберите матч')

async def darts_playoff_choose_match_handler(callback: CallbackQuery,
                                             button: Button,
                                             dialog_manager: DialogManager,
                                             playoff_id: str):
    dialog_manager.dialog_data['darts_playoff_match_id'] = int(playoff_id)

    await dialog_manager.switch_to(DartsStates.playoff_process_match)
    await callback.answer('Матч выбран')


async def darts_playoff_choose_first_player_handler(call: CallbackQuery,
                                                    button: Button,
                                                    dialog_manager: DialogManager,
                                                    player_id: str):
    """
    Обработчик выбора первого игрока в дартс-плейофф.
    """
    player_id = int(player_id)
    dialog_manager.dialog_data['darts_playoff_first_player_id'] = player_id

    await dialog_manager.next()
    await call.answer('Первый игрок выбран')


async def darts_playoff_choose_second_player_handler(call: CallbackQuery,
                                                    button: Button,
                                                    dialog_manager: DialogManager,
                                                    player_id: str):
    """
    Обработчик выбора второго игрока в дартс-плейофф.
    """
    player_id = int(player_id)
    dialog_manager.dialog_data['darts_playoff_second_player_id'] = player_id

    await dialog_manager.next()
    await call.answer('Второй игрок выбран')


async def darts_playoff_choose_type_handler(call: CallbackQuery,
                                            button: Button,
                                            dialog_manager: DialogManager,
                                            type_identifier: str):
    """
    Обработчик выбора типа матча в дартс-плейофф.
    """
    dialog_manager.dialog_data['darts_playoff_type_id'] = type_identifier
    logger.debug(f'Выбран тип матча: {type_identifier}')

    await dialog_manager.next()
    await call.answer('Тип матча выбран')


async def darts_playoff_confirm_start_match_handler(call: CallbackQuery,
                                                    button: Button,
                                                    dialog_manager: DialogManager):
    """
    Обработчик подтверждения начала матча в дартс-плейофф.

    создает запись в таблице игр playoff
    """
    session = dialog_manager.middleware_data['session']
    first_player_id = dialog_manager.dialog_data['darts_playoff_first_player_id']
    second_player_id = dialog_manager.dialog_data['darts_playoff_second_player_id']
    match_type = dialog_manager.dialog_data['darts_playoff_type_id']

    match_type_ = DartsPlayoffType.__dict__['_member_map_'][match_type]
    playoff_match = await create_darts_playoff_match(session, first_player_id, second_player_id, match_type_)

    playoff_id = playoff_match.playoff_id

    # TODO: add playoff_id if use button Back
    dialog_manager.dialog_data['darts_playoff_match_id'] = playoff_id

    await dialog_manager.next()
    await call.answer('Матч начат!')


async def add_darts_playoff_wins_handler(call: CallbackQuery,
                                         button: Button,
                                         dialog_manager: DialogManager,
                                         player_id: str):

    session = dialog_manager.middleware_data['session']
    player_id = int(player_id)
    playoff_id = dialog_manager.dialog_data['darts_playoff_match_id']

    await increment_player_win(session, playoff_id, player_id)

    await dialog_manager.switch_to(DartsStates.playoff_process_match)
    await call.answer('Очко добавлено')


async def darts_playoff_finish_match_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    playoff_id = dialog_manager.dialog_data['darts_playoff_match_id']
    player1_id = str(dialog_manager.dialog_data['darts_playoff_first_player_id'])
    player2_id = str(dialog_manager.dialog_data['darts_playoff_second_player_id'])
    playoff_players = dialog_manager.dialog_data['darts_playoff_players']
    player1_name = playoff_players[player1_id]['name']
    player2_name = playoff_players[player2_id]['name']

    await update_playoff_winner(session, playoff_id)

    await call.message.answer(f'Матч <b>{player1_name} - {player2_name}</b> завершен')

    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)
    await call.answer('Матч завершен')