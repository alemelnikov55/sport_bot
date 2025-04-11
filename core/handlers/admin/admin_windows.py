from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select, Back
from aiogram_dialog.widgets.text import Const, Format

from handlers.admin.admin_handlers import fix_score_handler, choose_sport_to_fix_handler, choose_team_to_fix_handler, \
    choose_match_to_fix_handler, choose_goal_to_fix_handler, admin_fix_goal_approve_handler, \
    admin_fix_goal_refuse_handler, back_admin_choose_goal_to_fix, \
    back_admin_choose_match_to_fix, back_admin_choose_team_to_fix, back_admin_choose_sport_to_fix
from handlers.admin.admin_getters import football_teams_getter, football_matches_getter, football_goal_getter, \
    admin_fix_goal_approve_getter
from handlers.judge.main_getters import get_sports
from handlers.judge.state import AdminStates


def get_admin_start_window() -> Window:
    return Window(
        Const("Главное меню админа"),
        Button(Const("Корректировка счета"), id="admin_fix_score", on_click=fix_score_handler),
        state=AdminStates.start_menu,
    )


def get_admin_choose_sport_to_fix_window() -> Window:
    return Window(
        Const('Корректировка счета\nВыберите дисциплину для корректировки'),
        Group(
            Select(
                Format('{item[name]}'),
                id='sport',
                item_id_getter=lambda item: item['name'],
                items='sports',
                on_click=choose_sport_to_fix_handler
            ),
            Button(Const('Назад'), id='back_admin_choose_sport_to_fix', on_click=back_admin_choose_sport_to_fix),
            width=2,
        ),
        state=AdminStates.choose_sport_to_fix,
        getter=get_sports
    )


def get_admin_choose_team_to_fix_window() -> Window:
    return Window(
        Const('Корректировка счета\nВыберите команду для корректировки'),
        Group(
            Select(
                Format('{item[name]}'),
                id='choose_team',
                item_id_getter=lambda item: item['id'],
                items='teams',
                on_click=choose_team_to_fix_handler
            ),
            width=2,
        ),
        Button(Const('Назад'), id='back_admin_choose_team_to_fix', on_click=back_admin_choose_team_to_fix),
        state=AdminStates.football_choose_team_to_fix,
        getter=football_teams_getter
    )


def get_admin_choose_match_to_fix_window() -> Window:
    return Window(
        Const('Корректировка счета\nВыберите матч для корректировки'),
        Group(
            Select(
                Format('{item[button_text]}'),
                id='choose_match',
                item_id_getter=lambda item: item['match_id'],
                items='matches',
                on_click=choose_match_to_fix_handler
            ),
            width=1,
        ),
        Button(Const('Назад'), id='back', on_click=back_admin_choose_match_to_fix),
        getter=football_matches_getter,
        state=AdminStates.football_choose_match_to_fix
    )


def get_admin_choose_goal_to_fix_window() -> Window:
    return Window(
        Const('Корректировка счета\nВыберите гол для корректировки'),
        Group(
            Select(
                Format('{item[scorer]}'),
                id='goal_to_fix',
                item_id_getter=lambda item: item['id'],
                items='goals',
                on_click=choose_goal_to_fix_handler
            ),
            width=1,
        ),
        Button(Const('Назад'), id='back_admin_choose_goal_to_fix', on_click=back_admin_choose_goal_to_fix),
        state=AdminStates.football_choose_goal_to_fix,
        getter=football_goal_getter
    )


def get_admin_fix_goal_approve_window() -> Window:
    return Window(
        Format('Вы действительно хотите отменить гол команды {team_name}\nВ матче {march_name}'),
        Group(
            Button(Const('Да'), id='approve', on_click=admin_fix_goal_approve_handler),
            Button(Const('Нет'), id='back', on_click=admin_fix_goal_refuse_handler),
            width=2,
        ),
        state=AdminStates.football_fix_goal_approve,
        getter=admin_fix_goal_approve_getter
    )


