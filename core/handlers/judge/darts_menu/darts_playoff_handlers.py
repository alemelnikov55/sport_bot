import logging
from pprint import pprint

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button
from requests import session

from database.darts_requests import create_darts_playoff_match
from database.models import DartsPlayoffType

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
    """
    session = dialog_manager.middleware_data['session']
    first_player_id = dialog_manager.dialog_data['darts_playoff_first_player_id']
    second_player_id = dialog_manager.dialog_data['darts_playoff_second_player_id']
    match_type = dialog_manager.dialog_data['darts_playoff_type_id']

    match_type_ = DartsPlayoffType.__dict__['_member_map_'][match_type]

    await create_darts_playoff_match(session, first_player_id, second_player_id, match_type_)

    await dialog_manager.next()
    await call.answer('Матч начат!')