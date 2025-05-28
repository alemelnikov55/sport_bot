import logging

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from handlers.judge.state import FootballStates, VolleyballStates, PongStates, RunStates, TugStates, RelayStates, \
    KettleStates, DartsStates

logger = logging.getLogger(__name__)


async def choose_sport_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, sport_id: str):
    """Обработчик выбора видов спорта"""
    await call.answer('Выбран спорт!')
    sports_arr = dialog_manager.dialog_data['sports']
    revert_sports = {str(item['id']): item['name'] for item in sports_arr}
    sport_name = revert_sports[sport_id]

    start_data = {'sport_name': sport_name,
                  'sport_id': int(sport_id),
                  'judge_telegram_id': call.message.chat.id}

    if sport_name == 'Мини-Футбол':
        await dialog_manager.start(FootballStates.match,
                                   data=start_data)

    elif sport_name == 'Волейбол':
        await dialog_manager.start(VolleyballStates.match,
                                   data=start_data)

    elif sport_name == 'Настольный теннис':
        await dialog_manager.start(PongStates.match,
                                   data=start_data)

    elif sport_name in ('Бег 100 м', 'Бег 2000 м', 'Бег 3000 м'):
        await dialog_manager.start(RunStates.get_runner_number,
                                   data=start_data)

    elif sport_name == 'Перетягивание каната':
        await dialog_manager.start(TugStates.match,
                                   data=start_data)

    elif sport_name == 'Эстафета 4 х 100 м':
        await dialog_manager.start(RelayStates.choose_team,
                                   data=start_data)

    elif sport_name == 'Гиревой спорт':
        await dialog_manager.start(KettleStates.choose_team,
                                   data=start_data)

    elif sport_name == 'Дартс':
        await dialog_manager.start(DartsStates.choose_team,
                                   data=start_data)

    else:
        logger.error(f'Неизвестный вид спорта: {sport_name}')
