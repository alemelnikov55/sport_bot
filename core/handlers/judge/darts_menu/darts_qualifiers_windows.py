from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.darts_menu.darts_qualifiers_getters import darts_team_choose_qualifiers_getter, darts_player_choose_getter, \
    darts_confirm_result_qualifiers_getter, darts_history_getter
from handlers.judge.darts_menu.darts_qualifiers_handlers import history_darts_handler, \
    darts_team_choose_handler, back_darts_to_choose_team_handler, darts_player_choose_qualifiers_handler, \
    back_to_choose_team_darts_handler, darts_score_input_qualifiers_handler, darts_confirm_result_qualifiers_handler, \
    darts_playoff_start_handler
from handlers.judge.state import DartsStates


def get_darts_team_choose_qualifiers_window() -> Window:
    return Window(
        Const("Выберите команду:"),
        Group(
            Select(
                Format("{item[name]}"),
                id="darts_team_choose_qualifiers",
                item_id_getter=lambda team: team['id'],
                items='darts_teams',
                on_click=darts_team_choose_handler,
            ),
            width=2
        ),
        Button(Const('История'), id='kettle_history', on_click=history_darts_handler),
        Button(Const('Play-off'), id='darts_playoff', on_click=darts_playoff_start_handler),
        Button(Const('Назад'), id='back_kettle_team_choose', on_click=back_darts_to_choose_team_handler),
        state=DartsStates.choose_team,
        getter=darts_team_choose_qualifiers_getter
    )


def get_darts_choose_player_qualifiers_window() -> Window:
    return Window(
        Const('Выберите игрока:'),
        Group(
            Select(
                Format("{item[name]}"),
                id='darts_choose_player',
                item_id_getter=lambda item: item["id"],
                items='players',
                on_click=darts_player_choose_qualifiers_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_darts_choose_player", on_click=back_to_choose_team_darts_handler),
        state=DartsStates.choose_player,
        getter=darts_player_choose_getter
    )


def get_darts_get_score_qualifiers_window() -> Window:
    return Window(
        Const('Введите результат:'),
        MessageInput(darts_score_input_qualifiers_handler),
        Button(Const("Назад"), id="back_darts_choose_player", on_click=back_to_choose_team_darts_handler),
        state=DartsStates.get_score,
    )


def get_darts_confirm_result_qualifiers_window() -> Window:
    return Window(
        Format('Подтвердите запись:\n'
               '<b>Спортсмен:</b> {player_name}\n'
               '<b>Результат:</b> {darts_scores} очков'),
        Button(Const("Записать"), id="confirm_kettle", on_click=darts_confirm_result_qualifiers_handler),
        Button(Const("Отменить"), id="reject_confirm_kettle", on_click=back_to_choose_team_darts_handler),
        state=DartsStates.confirm_score,
        getter=darts_confirm_result_qualifiers_getter)


def get_darts_history_window() -> Window:
    return Window(
        Format('Последние 6 добавленных записей:\n{history}'),
        Button(Const('Назад'), id='back_darts_history', on_click=back_to_choose_team_darts_handler),
        state=DartsStates.inpout_history,
        getter=darts_history_getter
    )



