from aiogram_dialog.widgets.input import MessageInput


from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.run_menu.run_getters import run_time_register_getter, run_time_confirm_getter, \
    run_history_getter
from handlers.judge.run_menu.run_handlers import runner_number_handler, back_run_result_register_handler, \
    history_runners_handler, back_run_time_register_handler, runner_result_handler, back_run_history_handler, \
    cancel_run_confirm_result_handler, run_confirm_result_handler
from handlers.judge.state import RunStates


def get_run_result_register_window() -> Window:
    return Window(
        Const('Введите номер спортсмена'),
        MessageInput(runner_number_handler),
        Button(Const('История'), id="last_runners", on_click=history_runners_handler),
        Button(Const("Назад"), id="back_register_run", on_click=back_run_result_register_handler),
        state=RunStates.get_runner_number,
    )


def get_run_time_register_window() -> Window:
    return Window(
        Format('Для <b>{runner_name} {runner_id}</b> введите результаты забега <b>{distance}</b>'),
        MessageInput(runner_result_handler),
        Button(Const("Назад"), id="back_register_run", on_click=back_run_time_register_handler),
        getter=run_time_register_getter,
        state=RunStates.get_runner_time
    )


def get_run_confirm_result_window() -> Window:
    return Window(
        Format('Подтвердите запись:\n'
               '<b>Спортсмен:</b> {runner_name} {runner_id}\n'
               '<b>Дистанция:</b> {distance}\n'
               '<b>Результат:</b> {runner_time} c'),
        Button(Const("Записать"), id="confirm_run", on_click=run_confirm_result_handler),
        Button(Const("Отменить"), id="back_confirm_run", on_click=cancel_run_confirm_result_handler),
        state=RunStates.confirm_runner_time,
        getter=run_time_confirm_getter
    )


def get_run_history_window() -> Window:
    return Window(
        Format('Последние 6 добавленных записей в забеге на {distance}:\n{history}'),
        Button(Const('Назад'), id='back_run_history', on_click=back_run_history_handler),
        state=RunStates.inpout_history,
        getter=run_history_getter
    )
