from magic_filter import F
from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select, Back
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.kettle_manu.kettle_getters import kettle_team_choose_getter, kettle_choose_lifter_getter
from handlers.judge.kettle_manu.kettle_handlers import history_kettle_handler, back_kettle_team_choose_handler, \
    kettle_team_choose_handler, back_kettle_choose_lifter_handler, kettle_choose_lifter_handler
from handlers.judge.state import KettleStates


def get_kettle_team_choose_window() -> Window:
    return Window(
        Const("Выберите команду:"),
        Group(
            Select(
                Format("{item[name]}"),
                id="kettle_team_choose",
                item_id_getter=lambda team: team['id'],
                items='kettle_teams',
                on_click=kettle_team_choose_handler,
            ),
            width=2
        ),
        Button(Const('История'), id='kettle_history', on_click=history_kettle_handler),
        Button(Const('Назад'), id='back_kettle_team_choose', on_click=back_kettle_team_choose_handler),
        state=KettleStates.choose_team,
        getter=kettle_team_choose_getter
    )


def get_kettle_choose_lifter_window() -> Window:
    return Window(
        Const('Выберите атлета:'),
        Group(
            Select(
                Format("{item[name]}"),
                id='kettle_choose_lifter',
                item_id_getter=lambda item: item["id"],
                items='players',
                on_click=kettle_choose_lifter_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_kettle_choose_lifter", on_click=back_kettle_choose_lifter_handler),
        state=KettleStates.chose_lifter,
        getter=kettle_choose_lifter_getter
    )

