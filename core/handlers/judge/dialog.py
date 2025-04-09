from aiogram import Router

from aiogram_dialog import Dialog

from handlers.judge.main_windows import get_sports_window
from handlers.judge.football_menu.windows import get_matches_window, get_start_match_window, get_process_window, \
    get_choose_scorer_window, get_finish_match_window, get_manual_match_create_window_1, \
    get_manual_match_create_window_2
from handlers.judge.volleyball_menu.volleyball_windows import get_volleyball_matches_window, \
    get_volleyball_start_match_window, get_volleyball_process_window, get_volleyball_finish_set_window, \
    get_volleyball_manual_add_match_window_2, get_volleyball_manual_add_match_window_1, \
    get_volleyball_finish_match_window

dialog_router = Router()

football_dialog = Dialog(
    get_matches_window(),
    get_start_match_window(),
    get_process_window(),
    get_choose_scorer_window(),
    get_finish_match_window(),

    get_manual_match_create_window_1(),
    get_manual_match_create_window_2()
)

volleyball_dialog = Dialog(
    get_volleyball_matches_window(),
    get_volleyball_start_match_window(),
    get_volleyball_process_window(),
    get_volleyball_manual_add_match_window_1(),
    get_volleyball_manual_add_match_window_2(),

    get_volleyball_finish_match_window(),
    get_volleyball_finish_set_window()
)


main_judge_dialog = Dialog(get_sports_window())


dialog_router.include_router(main_judge_dialog)
dialog_router.include_router(football_dialog)
dialog_router.include_router(volleyball_dialog)
