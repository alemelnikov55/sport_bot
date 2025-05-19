import logging

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button

from database.run_requests import save_running_result
from database.service_requests import get_participants_by_id
from handlers.judge.state import MainJudgeStates, RunStates

logger = logging.getLogger(__name__)


def parse_time_to_seconds(time_str: str) -> float:
    """
    Преобразует строку времени в секунды (float).
    Поддерживает формат HH:MM:SS.ss или H M S.ss (через пробелы).

    :param time_str: строка с временем
    :return: время в секундах как float
    """
    import re

    try:
        # Поддержка разделителей: и пробелов
        parts = re.split(r"[:\s]+", time_str.strip())
        decimal = float(f'0.{parts[-1]}')
        parts = [int(p) for p in parts[:-1] if p.strip() != ""]
        if len(parts) == 2:
            minutes, seconds = parts
        elif len(parts) == 1:
            hours = 0
            minutes = 0
            seconds = parts[0]
        else:
            raise ValueError("Неверный формат времени")

        total_seconds = float(minutes * 60 + seconds) + decimal
        return round(total_seconds, 2)

    except Exception as e:
        raise ValueError(f"Ошибка при разборе времени '{time_str}': {e}")


def format_seconds_to_time_string(seconds: float) -> str:
    """
    Преобразует количество секунд в строку без ведущих нулей.
    Примеры:
        3723.56 -> "1:2:3.56"
        62.34   -> "1:2.34"
        12.65   -> "12.65"

    :param seconds: время в секундах
    :return: строка с форматированным временем
    """
    try:
        total_seconds = round(seconds, 2)
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        sec = round(total_seconds % 60, 2)

        if hours > 0:
            return f"{hours}:{minutes}:{sec:05.2f}"
        elif minutes > 0:
            return f"{minutes}:{sec:05.2f}"
        else:
            return f"{sec:.2f}"

    except Exception as e:
        raise ValueError(f"Ошибка при форматировании времени: {e}")


async def runner_number_handler(message: Message, message_inpout: MessageInput,
                                               dialog_manager: DialogManager):
    try:
        runner_id = int(message.text.strip())
    except ValueError:
        await message.answer('В номере должны быть только цифры, попробуйте еще раз')
        return

    session = dialog_manager.middleware_data['session']
    runner = await get_participants_by_id(session, runner_id)

    if runner is None:
        await message.answer('Такого спортсмена нет, попробуйте еще раз')
        return

    dialog_manager.dialog_data['runner_id'] = runner.participant_id
    dialog_manager.dialog_data['runner_name'] = runner.short_name

    await dialog_manager.switch_to(RunStates.get_runner_time)


async def runner_result_handler(message: Message, message_inpout: MessageInput,
                                dialog_manager: DialogManager):
    raw_time = message.text.strip()
    dialog_manager.dialog_data['runner_time'] = parse_time_to_seconds(raw_time)

    await dialog_manager.switch_to(RunStates.confirm_runner_time)


async def run_confirm_result_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    runner_id = int(dialog_manager.dialog_data['runner_id'])
    sport_name = dialog_manager.start_data['sport_name']
    print(sport_name.split(' ')[:-2])
    distance = int(sport_name.split(' ')[-2])
    time = dialog_manager.dialog_data['runner_time']
    judge_id = call.message.chat.id

    await save_running_result(session, runner_id, time, distance, judge_id)

    await dialog_manager.switch_to(RunStates.get_runner_number)
    await call.answer('Запись сохранена!')


async def history_runners_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RunStates.inpout_history)


async def cancel_run_confirm_result_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RunStates.get_runner_number)
    await call.answer('Запись отменена')


async def back_run_time_register_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RunStates.get_runner_number)
    await call.answer('Назад!')


async def back_run_result_register_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(MainJudgeStates.sport)
    await call.answer('Назад!')


async def back_run_history_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(RunStates.get_runner_number)
    await call.answer('Назад!')
