from aiogram_dialog.widgets.input import MessageInput

from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, Select
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.kettle_manu.kettle_getters import kettle_team_choose_getter, kettle_choose_lifter_getter, \
    kettle_count_getter, kettle_confirm_result_getter, kettle_history_getter
from handlers.judge.kettle_manu.kettle_handlers import history_kettle_handler, back_kettle_team_choose_handler, \
    kettle_team_choose_handler, kettle_choose_lifter_handler, lifter_result_handler, \
    kettle_choose_category_handler, kettle_confirm_result_handler, back_to_choose_team, lifter_weight_handler
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
        Button(Const("Назад"), id="back_kettle_choose_lifter", on_click=back_to_choose_team),
        state=KettleStates.chose_lifter,
        getter=kettle_choose_lifter_getter
    )


def get_lifter_weight_window() -> Window:
    return Window(
        Const('Введите вес атлета:'),
        # Group(
        #     Select(
        #         Format("{item[category]}"),
        #         id="kettle_choose_category",
        #         item_id_getter=lambda item: item['category'],
        #         items='categories',
        #         on_click=kettle_choose_category_handler
        #     ),
        #     width=1
        # ),
        MessageInput(lifter_weight_handler),
        Button(Const('Назад'), id='back_get_weight', on_click=back_to_choose_team),
        state=KettleStates.get_weight,
        # getter=kettle_choose_category_getter
    )


def get_kettle_count_window() -> Window:
    return Window(
        Format('Введите число поднятий для:\n'
               '<b>{lifter_name}</b>\nВесовая категория: <b>{weight}</b>\nвозраст: <b>{age}</b>'),
        MessageInput(lifter_result_handler),
        Button(Const('Назад'), id='back_kettle_count', on_click=back_to_choose_team),
        state=KettleStates.get_lift_count,
        getter=kettle_count_getter
    )


def get_kettle_confirm_result_window() -> Window:
    return Window(
        Format('Подтвердите запись:\n'
               '<b>Спортсмен:</b> {lifter_name}\n'
               '<b>Весовая категория:</b> {weight}\n'
               '<b>Результат:</b> {lift_count} поднятий'),
        Button(Const("Записать"), id="confirm_kettle", on_click=kettle_confirm_result_handler),
        Button(Const("Отменить"), id="back_confirm_kettle", on_click=back_to_choose_team),
        state=KettleStates.confirm_lift_count,
        getter=kettle_confirm_result_getter
    )


def get_kettle_history_window() -> Window:
    return Window(
        Format('Последние 6 добавленных записей:\n{history}'),
        Button(Const('Назад'), id='back_kettle_history', on_click=back_to_choose_team),
        state=KettleStates.inpout_history,
        getter=kettle_history_getter
    )