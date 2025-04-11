from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.football_menu.getters import active_matches_getter, start_match_getter, match_info_getter, \
    choose_scorer_getter, football_teams_getter, teams_info_getter, choose_faller_getter
from handlers.judge.state import FootballStates
from handlers.judge.football_menu.handlers import choose_match_handler, start_match_handler, add_goal_handler, \
    finish_match_handler, choose_scorer_handler, choose_match_back_handler, confirm_finish_match_handler, \
    manual_football_match_add_handler, first_team_select_handler, second_team_select_handler, \
    back_start_football_match_handler, back_process_match_handler, back_choose_scorer_handler, \
    back_finish_match_handler, back_manual_match_create_2_handler, back_manual_match_create_1_handler, red_card_handler, \
    red_card_team_select_handler, red_card_player_select_handler


def get_matches_window() -> Window:
    """Окно выбора матча"""
    return Window(
        Const('Выберите матч:'),
        Group(
            Select(
                Format("{item[team1]} - {item[team2]}"),
                id="matches_select",
                item_id_getter=lambda item: item["match_id"],
                items="matches",
                on_click=choose_match_handler
            ),
            Button(Const("Создать матч"), id="manual_match_add", on_click=manual_football_match_add_handler),
            Button(Const("Назад"), id="back_choose_match", on_click=choose_match_back_handler),
            width=1,
            id="matches_group"
        ),
        state=FootballStates.match,
        getter=active_matches_getter
    )


def get_start_match_window() -> Window:
    return Window(
        Format("Начать матч {match[team1_name]} {match[team1_score]} - {match[team2_score]} {match[team2_name]}?"),
        Button(Const("Начать матч"),
               id="start_match",
               on_click=start_match_handler),
        Button(Const("Назад"), id="back_start_match", on_click=back_start_football_match_handler),
        state=FootballStates.start_match,
        getter=start_match_getter
    )


def get_process_window() -> Window:
    return Window(
        Format(
            'Идет матч:\n<b>{match[team1_name]} {match[team1_score]} : {match[team2_score]} {match[team2_name]}</b>'),
        Group(
            Select(
                Format('{item[name]}'),
                id="team_goal_select",
                item_id_getter=lambda item: item["id"],
                items='teams',
                on_click=add_goal_handler
            ),
            id='team_goal_group',
            width=2
        ),
        Button(Const('Закончить матч'), id='finish_match', on_click=finish_match_handler),
        Button(Const('RED CARD 🟥'), id='red_card', on_click=red_card_handler),
        Button(Const("Назад"), id="back_process_match", on_click=back_process_match_handler),
        state=FootballStates.process_match,
        getter=match_info_getter
    )


def get_choose_scorer_window() -> Window:
    return Window(
        Const('Выберите игрока, забившего гол:'),
        Group(
            Select(
                Format('{item[name]} {item[id]}'),
                id="scorer_select",
                item_id_getter=lambda item: item["id"],
                items='participants',
                on_click=choose_scorer_handler
            ),
            id='scorer_select_group',
            width=2,
        ),
        Button(Const("Назад"), id="back_choose_scorer", on_click=back_choose_scorer_handler),
        state=FootballStates.choose_scorer,
        getter=choose_scorer_getter
    )


def get_finish_match_window() -> Window:
    return Window(
        Format('Завершить матч: {match[team1_name]} {match[team1_score]} : {match[team2_score]} {match[team2_name]}?'),
        Button(Const("Подтвердить завершение матча"), id="finish_match", on_click=confirm_finish_match_handler),
        Button(Const("Назад"), id="back_finish_match", on_click=back_finish_match_handler),
        getter=match_info_getter,
        state=FootballStates.confirm_finish_match
    )


def get_manual_match_create_window_1() -> Window:
    return Window(
        Const("Выберите команду 1"),
        Group(
            Select(
                Format("{item[name]}"),
                id="manual_match_create_1",
                item_id_getter=lambda item: item["id"],
                items='teams',
                on_click=first_team_select_handler
            ),
            id='manual_match_create_1_group',
            width=2,
        ),
        Button(Const("Назад"), id="back_choose_team_1", on_click=back_manual_match_create_1_handler),
        state=FootballStates.manual_match_create_1,
        getter=football_teams_getter
    )


def get_manual_match_create_window_2() -> Window:
    return Window(
        Const("Выберите команду 2"),
        Group(
            Select(
                Format("{item[name]}"),
                id="manual_match_create_2",
                item_id_getter=lambda item: item["id"],
                items='teams',
                on_click=second_team_select_handler
            ),
            id='manual_match_create_2_group',
            width=2,
        ),
        Button(Const("Назад"), id="back_choose_team_2", on_click=back_manual_match_create_2_handler),
        state=FootballStates.manual_match_create_2,
        getter=football_teams_getter
    )


def get_red_card_choose_team_window() -> Window:
    return Window(
        Const('Выберите команду нафолившего'),

        Group(
            Select(
                Format('{item[name]}'),
                id="red_card_select",
                item_id_getter=lambda item: item["id"],
                items='teams',
                on_click=red_card_team_select_handler
            ),
            id='red_card_team_group',
            width=2,
        ),
        Button(Const("Назад"), id="back_red_card", on_click=back_finish_match_handler),
        state=FootballStates.red_card_choose_team,
        getter=teams_info_getter
    )


def get_red_card_choose_player_window() -> Window:
    return Window(
        Const('Выберите игрока, нафолившего'),

        Group(
            Select(
                Format('{item[name]} {item[id]}'),
                id="red_card_player_select",
                item_id_getter=lambda item: item["id"],
                items='players',
                on_click=red_card_player_select_handler
            ),
            id='red_card_player_group',
            width=2,
        ),
        Button(Const("Назад"), id="back_red_card", on_click=back_finish_match_handler),
        getter=choose_faller_getter,
        state=FootballStates.red_card_choose_player
    )
