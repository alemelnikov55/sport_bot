from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Group, Select, Button, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from magic_filter import F

from handlers.judge.pong_menu.pong_getters import pong_matches_getter, pong_start_match_getter, pong_set_info_getter, \
    finish_pong_set_getter, pong_match_result_getter, pong_teams_getter, pong_players_getter, pong_set_group_getter
from handlers.judge.pong_menu.pong_handlers import select_pong_match, back_pong_matches_handler, \
    start_pong_matches_handler, continue_pong_matches_handler, back_pong_start_match_handler, \
    back_pong_progress_handler, add_pong_goal_handler, finish_pong_set_handler, back_pong_finish_set_handler, \
    confirm_pong_finish_set_handler, finish_pong_match_handler, confirm_finish_pong_match_handler, \
    back_pong_finish_match_handler, first_pong_team_select_handler, back_pong_manual_add_match, \
    pong_manual_match_add_handler, pong_player_select_handler, pong_set_group_handler
from handlers.judge.state import PongStates


def get_pong_matches_window() -> Window:
    return Window(
        Const('Выберите матч по настольному теннису'),
        ScrollingGroup(
            Select(
                Format('{item[group]}: {item[player1]} - {item[player2]} {item[status]}'),
                id='select_pong_matches',
                item_id_getter=lambda item: item['match_id'],
                items='pong_matches',
                on_click=select_pong_match
            ),
            id='pong_matches_select',
            width=1,
            height=8
        ),
        Button(Const("Создать матч"), id="pong_manual_match_add",
               on_click=pong_manual_match_add_handler),
        Button(Const('Назад'), id='back', on_click=back_pong_matches_handler),
        state=PongStates.match,
        getter=pong_matches_getter
    )


def get_pong_start_match_window() -> Window:
    return Window(
        Format('Начать матч: {pong_match[player1]} - {pong_match[player2]}'),
        Button(Const('Начать матч'), id='start_pong_match', on_click=start_pong_matches_handler,
               when=F['pong_match']['is_started']),
        Button(Const('Продолжить матч'), id='continue_pong_match',
               when=F['pong_match']['is_in_process'],
               on_click=continue_pong_matches_handler,),
        Button(Const('Назад'), id='back', on_click=back_pong_start_match_handler),
        state=PongStates.start_match,
        getter=pong_start_match_getter

    )


def get_pong_progress_window() -> Window:
    return Window(
        Format(
            'Cчет в матче: {team_score_data[player1_name]} {team_score_data[player1_score]} - {team_score_data[player2_score]} {team_score_data[player2_name]}\n'
            'Счет {set_number} сета: {team_score_data[player1_name]} {team_score_data[player1_set_score]} - {team_score_data[player2_set_score]} {team_score_data[player2_name]}'
            # 'Счет вот '
        ),
        Select(
            Format('{item[player_name]}'),
            id='pong_progress_select',
            item_id_getter=lambda item: item['player_id'],
            items='pong_match',
            on_click=add_pong_goal_handler,
        ),
        Button(Const('Завершить сет'), id="finish_volleyball_set", on_click=finish_pong_set_handler),
        Button(Const("Завершить матч"),
               id="finish_pong_match",
               on_click=finish_pong_match_handler),
        Button(Const('Назад'), id='back', on_click=back_pong_progress_handler),
        state=PongStates.process_set,
        getter=pong_set_info_getter
    )


def get_pong_finish_set_window() -> Window:
    return Window(
        Format(
            'Завершить {pong_set_number} сет: {pong_set[player1_name]} {pong_set[player1_score]} - '
            '{pong_set[player2_score]} {pong_set[player2_name]} ?'),
        Button(Const("Подтвердить завершение сета"),
               id="finish_pong_set",
               on_click=confirm_pong_finish_set_handler),
        Button(Const("Назад"), id="back_pong_finish_set",
               on_click=back_pong_finish_set_handler
               ),
        state=PongStates.finish_set,
        getter=finish_pong_set_getter
    )


def get_pong_finish_match_window() -> Window:
    return Window(
        Format(
            'Завершить матч?\n{match_result}'),
        Button(Const("Подтвердить завершение матча"),
               id="confirm_finish_pong_match",
               on_click=confirm_finish_pong_match_handler),
        Button(Const("Назад"), id="back_pong_finish_match",
               on_click=back_pong_finish_match_handler),
        state=PongStates.finish_match,
        getter=pong_match_result_getter
    )


def get_pong_manual_add_match_team_window_1() -> Window:
    """Окно ручного ввода матча по понгу"""
    return Window(
        Const('Выберите команду игрока'),
        Group(
            Select(
                Format("{item[name]}"),
                id="pong_match_create_player1",
                item_id_getter=lambda item: item["id"],
                items='teams',
                on_click=first_pong_team_select_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_pong_choose_team_1", on_click=back_pong_manual_add_match),
        state=PongStates.manual_match_create_team_1,
        getter=pong_teams_getter
    )


def get_pong_manual_add_match_player_window_1() -> Window:
    """Окно ручного ввода матча по понгу"""
    return Window(
        Const('Выберите игрока'),
        Group(
            Select(
                Format("{item[name]}"),
                id="pong_match_create_player1",
                item_id_getter=lambda item: item["id"],
                items='players',
                on_click=pong_player_select_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_choose_player_1", on_click=back_pong_manual_add_match),
        state=PongStates.manual_match_create_player_1,
        getter=pong_players_getter
    )


def get_pong_manual_set_group_window() -> Window:
    return Window(
        Const('Выберите тип матча:'),
        Group(
            Select(
                Format("{item[name]}"),
                id="pong_set_group",
                item_id_getter=lambda item: item["id"],
                items='groups',
                on_click=pong_set_group_handler
            ),
            width=2,
        ),
        Button(Const("Назад"), id="back_pong_set_group", on_click=back_pong_manual_add_match),
        state=PongStates.pong_set_group,
        getter=pong_set_group_getter
    )
