from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.relay_menu.relay_getter import relay_team_choose_getter, relay_time_register_getter, \
    relay_time_confirm_getter, relay_history_getter
from handlers.judge.relay_menu.relay_handlers import relay_team_choose_handler, back_relay_team_choose_handler, \
    back_relay_time_register_handler, relay_result_handler, cancel_relay_confirm_result_handler, \
    relay_confirm_result_handler, history_relay_handler, back_relay_history_handler
from handlers.judge.state import RelayStates


def get_relay_team_choose() -> Window:
    return Window(
        Const("Выберите команду:"),
        Group(
            Select(
                Format("{item[name]}"),
                id="relay_team_choose",
                item_id_getter=lambda team: team['id'],
                items='relay_teams',
                on_click=relay_team_choose_handler,
            ),
            width=2
        ),
        Button(Const('История'), id="relay_runners", on_click=history_relay_handler),
        Button(Const('Назад'), id='back_relay_team_choose', on_click=back_relay_team_choose_handler),
        state=RelayStates.choose_team,
        getter=relay_team_choose_getter
    )


def get_relay_time_register() -> Window:
    return Window(
        Format('Для команды <b>{relay_team}</b> введите результаты забега <b>{distance}</b>'),
        MessageInput(relay_result_handler),
        Button(Const("Назад"), id="back_register_run", on_click=back_relay_time_register_handler),
        getter=relay_time_register_getter,
        state=RelayStates.get_team_time
    )


def get_relay_confirm_result_window() -> Window:
    return Window(
        Format('Подтвердите запись:\n'
               '<b>Команда:</b> {relay_team}\n'
               '<b>Дистанция:</b> {distance}\n'
               '<b>Результат:</b> {relay_time} c'),
        Button(Const("Записать"), id="confirm_relay", on_click=relay_confirm_result_handler),
        Button(Const("Отменить"), id="back_confirm_relay", on_click=cancel_relay_confirm_result_handler),
        state=RelayStates.conform_team_time,
        getter=relay_time_confirm_getter
    )


def get_relay_history_window() -> Window:
    return Window(
        Format('Последние 6 добавленных записей в забеге на {distance}:\n{history}'),
        Button(Const('Назад'), id='back_run_history', on_click=back_relay_history_handler),
        state=RelayStates.inpout_history,
        getter=relay_history_getter
    )
