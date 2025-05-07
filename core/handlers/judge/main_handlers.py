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
    if sport_name == 'football':
        await dialog_manager.start(FootballStates.match)
    elif sport_name == 'volleyball':
        await dialog_manager.start(VolleyballStates.match)
    elif sport_name == 'pong':
        await dialog_manager.start(PongStates.match)
    elif sport_name in ('run_100m', 'run_2000m', 'run_3000m'):
        await dialog_manager.start(RunStates.get_runner_number,
                                   data={'sport_name': sport_name,
                                         'sport_id': sport_id,
                                         'judge_telegram_id': call.message.chat.id})
    elif sport_name == 'tug_of_war':
        await dialog_manager.start(TugStates.match,
                                   data={'sport_name': sport_name,
                                         'sport_id': sport_id,
                                         'judge_telegram_id': call.message.chat.id}
                                   )

    elif sport_name == 'relay_race_4x100':
        await dialog_manager.start(RelayStates.choose_team,
                                   data={'sport_name': sport_name,
                                         'sport_id': sport_id,
                                         'judge_telegram_id': call.message.chat.id}
                                   )
    elif sport_name == 'kettle':
        await dialog_manager.start(KettleStates.choose_team,
                                   data={'sport_name': sport_name,
                                         'sport_id': sport_id,
                                         'judge_telegram_id': call.message.chat.id}
                                   )
    elif sport_name == 'darts':
        await dialog_manager.start(DartsStates.choose_team,
                                   data={'sport_name': sport_name,
                                         'sport_id': sport_id,
                                         'judge_telegram_id': call.message.chat.id}
                                   )
    else:
        logger.error(f'Неизвестный вид спорта: {sport_name}')
