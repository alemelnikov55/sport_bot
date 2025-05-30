from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.darts_menu.darts_playoff_getters import darts_playoff_choose_first_player_getter, \
    darts_playoff_choose_type_getter, darts_playoff_confirm_start_match_getter, darts_playoff_process_match_getter, \
    darts_playoff_choose_match_getter
from handlers.judge.darts_menu.darts_playoff_handlers import darts_playoff_choose_first_player_handler, \
    darts_playoff_choose_second_player_handler, darts_playoff_choose_type_handler, \
    darts_playoff_confirm_start_match_handler, add_darts_playoff_wins_handler, darts_playoff_finish_match_handler, \
    darts_playoff_get_match_list_handler, darts_playoff_choose_match_handler
from handlers.judge.darts_menu.darts_qualifiers_handlers import back_to_choose_team_darts_handler
from handlers.judge.state import DartsStates


def get_darts_playoff_choose_first_player_window() -> Window:
    return Window(
        Const('Выберите первого игрока:'),
        Group(
            Select(
                Format("{item[name]} {item[scores]}"),
                id='darts_playoff_choose_first_player',
                item_id_getter=lambda item: item['player_id'],
                items='playoff_players',
                on_click=darts_playoff_choose_first_player_handler
            ),
            width=2
        ),
        Button(Const('Матчи Play-off'), id='darts_playoff_get_matches', on_click=darts_playoff_get_match_list_handler),
        Button(Const("Назад"), id="back_darts_playoff_choose_first_player", on_click=back_to_choose_team_darts_handler),
        state=DartsStates.playoff_choose_first_player,
        getter=darts_playoff_choose_first_player_getter
    )


def get_darts_playoff_choose_second_player_window() -> Window:
    return Window(
        Const('Выберите второго игрока:'),
        Group(
            Select(
                Format("{item[name]} {item[scores]}"),
                id='darts_playoff_choose_second_player',
                item_id_getter=lambda item: item['player_id'],
                items='playoff_players',
                on_click=darts_playoff_choose_second_player_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_darts_playoff_choose_second_player", on_click=back_to_choose_team_darts_handler),
        state=DartsStates.playoff_choose_second_player,
        getter=darts_playoff_choose_first_player_getter
    )


def get_darts_playoff_choose_match_window() -> Window:
    return Window(
        Const('Выберите из созданных матчей:'),
        Group(
            Select(
                Format("{item[player1_name]} {item[player1_wins]} - {item[player2_wins]} {item[player2_name]} {item[playoff_type]}"),
                id='darts_playoff_choose_match',
                item_id_getter=lambda item: item['playoff_id'],
                items='playoff_matches',
                on_click=darts_playoff_choose_match_handler
            ),
            width=1
        ),
        Button(Const('Назад'), id='back_darts_playoff_choose_match', on_click=back_to_choose_team_darts_handler),
        state=DartsStates.match_list,
        getter=darts_playoff_choose_match_getter
    )


def get_darts_playoff_type_window() -> Window:
    return Window(
        Const('Выберите тип матча:'),
        Group(
            Select(
                Format("{item[name]}"),
                id='darts_playoff_type',
                item_id_getter=lambda item: item['id'],
                items='playoff_types',
                on_click=darts_playoff_choose_type_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_darts_playoff_choose_first_player", on_click=back_to_choose_team_darts_handler),
        state=DartsStates.playoff_choose_type,
        getter=darts_playoff_choose_type_getter
    )


def get_darts_playoff_confirm_start_match_window() -> Window:
    return Window(
        Format('Подтвердите запись:\n'
               '<b>Первый игрок:</b> {first_player_name}\n'
               '<b>Второй игрок:</b> {second_player_name}\n'
               '<b>Тип матча:</b> {match_type}'),
        Button(Const('Подтвердить и начать'), id='darts_playoff_confirm_start_match', on_click=darts_playoff_confirm_start_match_handler),
        Button(Const('Назад'), id='back_darts_playoff_choose_first_player', on_click=back_to_choose_team_darts_handler),
        state=DartsStates.playoff_confirm_start_match,
        getter=darts_playoff_confirm_start_match_getter
    )

def get_darts_playoff_process_match_window() -> Window:
    return Window(
        Format('Счет в матче: {match_info[player_1][name]} {match_info[player_1][scores]} - {match_info[player_2][scores]} {match_info[player_2][name]}\n'
               'Идет {match_info[leg]} лег'),
        Select(
            Format('{item[name]}'),
            id='darts_playoff_process_match',
            item_id_getter=lambda item: item['player_id'],
            items='playoff_players',
            on_click=add_darts_playoff_wins_handler
        ),
        Button(Const('Завершить матч'), id='darts_playoff_finish_match', on_click=darts_playoff_finish_match_handler),
        Button(Const('Назад'), id='back_darts_playoff_process_match', on_click=back_to_choose_team_darts_handler),
        state=DartsStates.playoff_process_match,
        getter=darts_playoff_process_match_getter
    )
