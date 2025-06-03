from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from handlers.admin.admin_handlers import fix_score_handler, choose_sport_to_fix_handler, choose_team_to_fix_handler, \
    choose_match_to_fix_handler, choose_goal_to_fix_handler, admin_fix_goal_approve_handler, \
    admin_fix_goal_refuse_handler, back_admin_choose_sport_to_fix, \
    create_groups_handler, create_football_tournament_groups, groups_football_count_inpout_handler, \
    groups_volleyball_count_inpout_handler, create_volleyball_tournament_groups, add_judge_handler, \
    add_judge_inpout_handler, groups_pong_count_inpout_handler, create_pong_tournament_groups, \
    groups_tug_count_inpout_handler, create_tug_tournament_groups, admin_send_result_handler, send_result_handler, \
    back_to_panel_handler, pong_choose_gender_handler
from handlers.admin.admin_getters import football_matches_getter, football_goal_getter, \
    admin_fix_goal_approve_getter, create_groups_tournament_football_getter, create_groups_tournament_volleyball_getter, \
    create_groups_tournament_pong_getter, create_groups_tournament_tug_getter
from handlers.judge.football_menu.football_getters import football_teams_getter
from handlers.judge.main_getters import get_sports
from handlers.judge.state import AdminStates


def get_admin_start_window() -> Window:
    return Window(
        Const('Главное меню админа'),
        Button(Const('Корректировка счета'), id='admin_fix_score', on_click=fix_score_handler),
        Button(Const('Создание групп/матчей'), id='admin_create_groups', on_click=create_groups_handler),
        Button(Const('Добавить судью'), id='admin_add_judge', on_click=add_judge_handler),
        Button(Const('Отправить результаты'), id='admin_send_result', on_click=admin_send_result_handler),
        state=AdminStates.start_menu,
    )


def get_admin_add_judge_window() -> Window:
    return Window(
        Const('Введите id судьи'),
        MessageInput(add_judge_inpout_handler),
        state=AdminStates.add_judge,
    )


def get_create_groups_window() -> Window:
    return Window(
        Const('Создание групп'),
        Button(Const('Предварительные группы football'),
               id='create_groups_tournament_football', on_click=create_football_tournament_groups),
        Button(Const('Предварительные группы volleyball'),
               id='create_groups_tournament_volleyball', on_click=create_volleyball_tournament_groups),
        Button(Const('Предварительные группы pong'),
               id='create_groups_tournament_pong', on_click=create_pong_tournament_groups),
        Button(Const('Предварительные группы tug'),
               id='create_groups_tournament_tug', on_click=create_tug_tournament_groups),
        Button(Const('Назад'), id='back_admin_crete_groups', on_click=back_to_panel_handler),
        state=AdminStates.create_groups,
    )


def get_create_groups_tournament_football_window() -> Window:
    return Window(
        Format('Зарегистрировано {teams_count} футбольных команд.\nЧерез пробел введите число команд в каждой группе'),
        MessageInput(groups_football_count_inpout_handler),
        Button(Const('Назад'), id='back_create_groups_tournament_football', on_click=back_to_panel_handler),
        state=AdminStates.create_football_tournament_groups,
        getter=create_groups_tournament_football_getter
    )


def get_create_groups_tournament_volleyball_window() -> Window:
    return Window(
        Format(
            'Зарегистрировано {teams_count} волейбольных команд.\nЧерез пробел введите число команд в каждой группе'),
        MessageInput(groups_volleyball_count_inpout_handler),
        state=AdminStates.create_volleyball_tournament_groups,
        getter=create_groups_tournament_volleyball_getter
    )


def get_choose_gender_pong_groups() -> Window:
    return Window(
        Const('Выберите группу:'),
        Group(
            Button(Const('Мужская'), id='pong_choose_male', on_click=pong_choose_gender_handler),
            Button(Const('Женская'), id='pong_choose_female', on_click=pong_choose_gender_handler),
        ),
        state=AdminStates.choose_gender_pong
    )


def get_create_groups_tournament_pong_window() -> Window:
    return Window(
        Format(
            'Зарегистрировано {players_count} игроков в настольный тенис среди {gender}.\nЧерез пробел введите число игроков в каждой группе'),
        MessageInput(groups_pong_count_inpout_handler),
        Button(Const('Назад'), id='back_create_groups_tournament_pong', on_click=back_to_panel_handler),
        state=AdminStates.create_pong_tournament_groups,
        getter=create_groups_tournament_pong_getter
    )


def get_create_tug_tournament_groups_window() -> Window:
    return Window(
        Format(
            'Зарегистрировано {tug_team_count} команд в перетягивании.\nЧерез пробел введите число команд в каждой группе'),
        MessageInput(groups_tug_count_inpout_handler),
        Button(Const('Назад'), id='back_create_tug_tournament_groups', on_click=back_to_panel_handler),
        state=AdminStates.create_tug_tournament_groups,
        getter=create_groups_tournament_tug_getter
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
        Button(Const('Назад'), id='back_admin_choose_team_to_fix', on_click=back_to_panel_handler),
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
        Button(Const('Назад'), id='back', on_click=back_to_panel_handler),
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
        Button(Const('Назад'), id='back_admin_choose_goal_to_fix', on_click=back_to_panel_handler),
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
        Button(Const('Назад'), id='back_admin_fix_goal_approve', on_click=back_to_panel_handler),
        state=AdminStates.football_fix_goal_approve,
        getter=admin_fix_goal_approve_getter
    )


def get_admin_send_result_handler() -> Window:
    return Window(
        Const('Выберите дисциплину для отправки результатов:'),
        Button(Const('Отправить результаты забегов 100м, 2000м, 3000м.'), id='send_run_results', on_click=send_result_handler),
        Button(Const('Отправить результаты Эстафеты'), id='send_relay_results', on_click=send_result_handler),
        Button(Const('Отправить результаты по перетягиванию каната'), id='send_tug_results', on_click=send_result_handler),
        Button(Const('Отправить результаты по гиревому спорту'), id='send_kettle_results', on_click=send_result_handler),
        Button(Const('Отправить результаты по дартс'), id='send_darts_results', on_click=send_result_handler),
        Button(Const('Отправить результаты по настольному теннису'), id='send_pong_results', on_click=send_result_handler),
        Button(Const('Назад'), id='back_admin_send_result', on_click=back_to_panel_handler),
        state=AdminStates.send_result,
    )
