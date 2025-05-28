from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, Select, Back, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from magic_filter import F

from handlers.judge.state import TugStates
from handlers.judge.tug_menu.tug_getters import tug_matches_getter, start_tug_match_getter, tug_match_info_getter, \
    tug_finish_match_getter, tug_teams_getter, tug_set_group_getter
from handlers.judge.tug_menu.tug_handlers import choose_tug_match_handler, start_tug_match_handler, \
    continue_tug_match_handler, add_tug_goal_handler, finish_tug_match_handler, confirm_finish_tug_match_handler, \
    back_finish_tug_match_handler, back_tug_choose_match, \
    manual_tug_match_add_handler, first_tug_team_select_handler, second_tug_team_select_handler, \
    back_tug_choose_team_handler, tug_set_group_handler


def get_tug_choose_match_window() -> Window:
    return Window(
        Const('Выберите матч по перетягиванию каната:'),
        ScrollingGroup(
            Select(
                Format('{item[group]}: {item[team1_name]} - {item[team2_name]} {item[status]}'),
                id="tug_matches_select",
                item_id_getter=lambda item: item["pull_id"],
                items="tug_matches",
                on_click=choose_tug_match_handler
            ),
            width=1,
            height=10,
            id="tug_matches_group",
        ),
        Button(Const('Создать матч'), id='manual_tug_match_add', on_click=manual_tug_match_add_handler),
        Button(Const("Назад"), id='back_choose_tug_match', on_click=back_tug_choose_match),
        state=TugStates.match,
        getter=tug_matches_getter,
    )


def get_tug_start_match_window() -> Window:
    return Window(
        Format(
            'Начать матч {tug_match[team1_name]} {tug_match[team1_score]} - {tug_match[team2_score]} {tug_match[team2_name]}?'),
        Button(Const('Начать матч'), id='start_tug_match', on_click=start_tug_match_handler,
               when=F['tug_match']['is_started']),
        Button(Const('Продолжить матч'), id='continue_tug_match',
               when=F['tug_match']['is_in_process'],
               on_click=continue_tug_match_handler),
        Button(Const('Назад'), id='back_start_tug_match', on_click=back_tug_choose_team_handler),
        state=TugStates.start_match,
        getter=start_tug_match_getter
    )


def get_tug_process_window() -> Window:
    return Window(
        Format(
            'Матч по перетягиванию каната:\n{tug_match[team1_name]} {tug_match[team1_score]} - {tug_match[team2_score]} {tug_match[team2_name]}'),
        Group(
            Select(
                Format('{item[team_name]}'),
                id="tug_process_set",
                item_id_getter=lambda item: item["team_id"],
                items='only_teams_info',
                on_click=add_tug_goal_handler
            ),
            width=2,
        ),
        Button(Const("Завершить матч"),
               id="finish_tug_match",
               on_click=finish_tug_match_handler),
        Button(Const("Назад"), id="back_tug_process_set", on_click=back_tug_choose_team_handler),
        state=TugStates.process_match,
        getter=tug_match_info_getter
    )


def get_tug_finish_match_window() -> Window:
    return Window(
        Format('Завершить матч по перетягиванию:\n{tug_match[team1_name]} {tug_match[team1_score]} - {tug_match[team2_score]} {tug_match[team2_name]}'),
        Button(Const('Подтвердить'), id='confirm_finish_tug_match', on_click=confirm_finish_tug_match_handler),
        Button(Const('Назад'), id='back_finish_tug_match', on_click=back_finish_tug_match_handler),
        state=TugStates.confirm_finish_match,
        getter=tug_finish_match_getter
    )


def get_tug_manual_add_match_window_1() -> Window:
    return Window(
        Const('Выберите команду 1'),
        Group(
            Select(
                Format('{item[name]}'),
                id="tug_match_create_team1",
                item_id_getter=lambda item: item['id'],
                items='tug_teams',
                on_click=first_tug_team_select_handler
            ),
            width=1,
        ),
        Button(Const('Назад'), id='back_tug_manual', on_click=back_tug_choose_team_handler),
        state=TugStates.manual_match_create_1,
        getter=tug_teams_getter
    )


def get_tug_manual_add_match_window_2() -> Window:
    return Window(
        Const('Выберите команду 2 ✅'),
        Group(
            Select(
                Format('{item[name]}'),
                id='tug_match_create_team2',
                item_id_getter=lambda item: item['id'],
                items='tug_teams',
                on_click=second_tug_team_select_handler
            ),
            width=1,
        ),
        Button(Const('Назад'), id='back_tug_manual', on_click=back_tug_choose_team_handler),
        state=TugStates.manual_match_create_2,
        getter=tug_teams_getter
    )


def get_tug_set_group_window() -> Window:
    return Window(
        Const('Выберите тип матча:'),
        Group(
            Select(
                Format("{item[name]}"),
                id="tug_set_group",
                item_id_getter=lambda item: item["id"],
                items='groups',
                on_click=tug_set_group_handler
            ),
            width=2,
        ),
        Button(Const("Назад"), id="back_tug_set_group", on_click=back_tug_choose_team_handler),
        state=TugStates.set_group,
        getter=tug_set_group_getter
    )
