from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select, Back
from aiogram_dialog.widgets.text import Const, Format
from magic_filter import F

from handlers.judge.state import VolleyballStates
from handlers.judge.volleyball_menu.volleyball_getters import start_volleyball_match_getter, \
    volleyball_set_info_getter, finish_volleyball_set_getter, volleyball_teams_getter, volleyball_match_result_getter, \
    volleyball_matches_getter, volleyball_set_group_getter
from handlers.judge.volleyball_menu.volleyball_handlers import choose_volleyball_match_handler, \
    manual_volleyball_match_add_handler, start_volleyball_match_handler, add_volleyball_goal_handler, \
    finish_volleyball_set_handler, confirm_finish_volleyball_set_handler, \
    back_choose_match_handler, first_volleyball_team_select_handler, second_volleyball_team_select_handler, \
    finish_volleyball_match_handler, confirm_finish_volleyball_match_handler, back_volleyball_finish_set_handler, \
    back_volleyball_finish_match_handler, continue_volleyball_match_handler, \
    volleyball_set_group_handler, back_volleyball_to_choose_match_handler


def get_volleyball_matches_window() -> Window:
    """Окно выбора Волейбольного матча"""
    return Window(
        Const('Выберите матч:'),
        Group(
            Select(
                Format("{item[group]}: {item[team1]} - {item[team2]} {item[status]}"),
                id="volleyball_matches_select",
                item_id_getter=lambda item: item["match_id"],
                items="volleyball_matches",
                on_click=choose_volleyball_match_handler
            ),
            Button(Const("Создать матч"), id="manual_match_add", on_click=manual_volleyball_match_add_handler),
            Button(Const("Назад"), id="back_choose_match", on_click=back_choose_match_handler),
            width=1,
            id="volleyball_matches_group"
        ),
        state=VolleyballStates.match,
        getter=volleyball_matches_getter
    )


def get_volleyball_start_match_window() -> Window:
    """Окно подтвреждения начала волейбольного матча"""
    return Window(
        Format(
            'Начать матч {volleyball_match[team1_name]} {volleyball_match[team1_score]} - {volleyball_match[team2_score]} {volleyball_match[team2_name]}?'),
        Button(Const('Начать матч'), id='start_volleyball_match', on_click=start_volleyball_match_handler,
               when=F['volleyball_match']['is_started']),
        Button(Const('Продолжить матч'), id='continue_volleyball_match',
               when=F['volleyball_match']['is_in_process'],
               on_click=continue_volleyball_match_handler),
        Button(Const('Продолжить матч'), id='continue_volleyball_match',
               when=F['volleyball_match']['is_finished'],
               on_click=continue_volleyball_match_handler),
        Button(Const('Назад'), id='back_start_volleyball_match', on_click=back_volleyball_to_choose_match_handler),
        state=VolleyballStates.start_match,
        getter=start_volleyball_match_getter
    )


def get_volleyball_process_window() -> Window:
    """Окно процесса волейбольного матча"""
    return Window(
        Format(
            'Cчет в матче: {team_score_data[team1_name]} {team_score_data[team1_score]} - {team_score_data[team2_score]} {team_score_data[team2_name]}\n'
            'Счет {set_number} сета: {team_score_data[team1_name]} {team_score_data[tesm1_set_score]} - {team_score_data[tesm2_set_score]} {team_score_data[team2_name]}'
        ),
        Select(
            Format('{item[team_name]}'),
            id="volleyball_process_set",
            item_id_getter=lambda item: item["team_id"],
            items='volleyball_match',
            on_click=add_volleyball_goal_handler
        ),
        Button(Const('Завершить сет'), id="finish_volleyball_set", on_click=finish_volleyball_set_handler),
        Button(Const("Завершить матч"),
               id="finish_volleyball_match",
               on_click=finish_volleyball_match_handler),
        Button(Const("Назад"), id="back_volleyball_process_set", on_click=back_volleyball_to_choose_match_handler),
        state=VolleyballStates.process_set,
        getter=volleyball_set_info_getter
    )


def get_volleyball_finish_set_window() -> Window:
    """Окно окончания матча/сета волейбола"""
    return Window(
        Format(
            'Завершить {set_number} сет: {volleyball_set[team1_name]} {volleyball_set[tesm1_set_score]} - '
            '{volleyball_set[tesm2_set_score]} {volleyball_set[team2_name]} ?'),
        Button(Const("Подтвердить завершение сета"),
               id="finish_volleyball_set",
               on_click=confirm_finish_volleyball_set_handler),
        Button(Const("Назад"), id="back_volleyball_finish_set",
               on_click=back_volleyball_finish_set_handler
               ),
        state=VolleyballStates.finish_set,
        getter=finish_volleyball_set_getter
    )


def get_volleyball_finish_match_window() -> Window:
    return Window(
        Format(
            'Завершить матч?\n{match_result}'),
        Button(Const("Подтвердить завершение матча"),
               id="confirm_finish_volleyball_match",
               on_click=confirm_finish_volleyball_match_handler
               ),
        Button(Const("Назад"), id="back_volleyball_finish_match",
               on_click=back_volleyball_finish_match_handler
               ),
        state=VolleyballStates.finish_match,
        getter=volleyball_match_result_getter
    )


def get_volleyball_manual_add_match_window_1() -> Window:
    """Окно ручного ввода волейбольного матча"""
    return Window(
        Const('Выберите команду 1'),
        Group(
            Select(
                Format("{item[name]}"),
                id="volleyball_match_create_team1",
                item_id_getter=lambda item: item["id"],
                items='teams',
                on_click=first_volleyball_team_select_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_choose_team_2", on_click=back_volleyball_to_choose_match_handler),
        state=VolleyballStates.manual_match_create_1,
        getter=volleyball_teams_getter,
    )


def get_volleyball_manual_add_match_window_2() -> Window:
    """Окно ручного ввода волейбольного матча"""
    return Window(
        Const('Выберите команду 2'),
        Group(
            Select(
                Format("{item[name]}"),
                id="volleyball_match_create_team2",
                item_id_getter=lambda item: item["id"],
                items='teams',
                on_click=second_volleyball_team_select_handler
            ),
            width=2
        ),
        Button(Const("Назад"), id="back_manual_match_create", on_click=back_volleyball_to_choose_match_handler),
        state=VolleyballStates.manual_match_create_2,
        getter=volleyball_teams_getter,
    )


def get_volleyball_set_group_windows() -> Window:
    return Window(
        Const('Выберите тип матча:'),
        Group(
            Select(
                Format("{item[name]}"),
                id="volleyball_set_group",
                item_id_getter=lambda item: item["id"],
                items='groups',
                on_click=volleyball_set_group_handler
            ),
            width=2,
        ),
        Button(Const("Назад"), id="back_volleyball_set_group", on_click=back_volleyball_to_choose_match_handler),
        state=VolleyballStates.manual_set_group,
        getter=volleyball_set_group_getter
    )