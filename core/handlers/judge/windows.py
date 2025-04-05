from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup, Select, Calendar, CalendarConfig, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.getters import get_sports, active_matches_getter, start_match_getter, match_info_getter, \
    choose_scorer_getter
from handlers.judge.state import FootballStates
from handlers.judge.handlers import choose_sport_handler, choose_match_handler, start_match_handler, add_goal_handler, \
    finish_match_handler, choose_scorer_handler, choose_match_back_handler


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
            Back(Const("Назад"), id="back_choose_match", on_click=choose_match_back_handler),
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
        Back(Const("Назад"), id="back_start_match"),
        state=FootballStates.start_match,
        getter=start_match_getter
    )


def get_process_window() -> Window:
    return Window(
        Format('Идет матч:\n<b>{match[team1_name]} {match[team1_score]} : {match[team2_score]} {match[team2_name]}</b>'),
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
        # Group(
        #     Button(Format('{match[team1_name]}'), id='add_goal', on_click=add_goal_handler),
        #     Button(Format('{match[team2_name]}'), id='add_goal', on_click=add_goal_handler),
        #     width=2,
        #     id='process_match_group'
        # ),
        Button(Const('Закончить матч'), id='finish_match', on_click=finish_match_handler),
        Back(Const("Назад"), id="back_process_match"),
        state=FootballStates.goal,
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
        Back(Const("Назад"), id="back_choose_scorer"),
        state=FootballStates.choose_scorer,
        getter=choose_scorer_getter
    )


def get_finish_match_window() -> Window:
    return Window(
        Format('Завершить матч: {match[team1_name]} {match[team1_score]} : {match[team2_score]} {match[team2_name]}?'),
        Button(Const("Подтвердить завершение матча"), id="finish_match", on_click=finish_match_handler),
        getter=match_info_getter,
        state=FootballStates.finish_match
    )
#
#
# def get_manual_match_create_window() -> Window:
#     return Window(
#
#     )