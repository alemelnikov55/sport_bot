from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Group, Select
from aiogram_dialog.widgets.text import Const, Format

from handlers.judge.main_getters import get_sports
from handlers.judge.main_handlers import choose_sport_handler
from handlers.judge.state import MainJudgeStates


def get_sports_window() -> Window:
    """Окно выбора спорта"""
    return Window(
        Const('Выберите дисциплину:'),
        Group(
            Select(
                Format("{item[name]}"),
                id="sport_select",
                item_id_getter=lambda item: item["id"],
                items="sports",
                on_click=choose_sport_handler,
            ),
            width=2,  # 2 кнопки в ряду
            id="sports_group"
        ),
        state=MainJudgeStates.sport,
        getter=get_sports
    )
