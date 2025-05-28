from aiogram import Router

from aiogram_dialog import Dialog

from handlers.admin.admin_windows import get_admin_start_window, get_admin_choose_sport_to_fix_window, \
    get_admin_choose_team_to_fix_window, get_admin_choose_match_to_fix_window, get_admin_choose_goal_to_fix_window, \
    get_admin_fix_goal_approve_window, get_create_groups_window, get_create_groups_tournament_football_window, \
    get_create_groups_tournament_volleyball_window, get_admin_add_judge_window, \
    get_create_groups_tournament_pong_window, get_create_tug_tournament_groups_window, get_admin_send_result_handler, \
    get_choose_gender_pong_groups
from handlers.judge.darts_menu.darts_playoff_windows import get_darts_playoff_choose_first_player_window, \
    get_darts_playoff_choose_second_player_window, get_darts_playoff_type_window, \
    get_darts_playoff_confirm_start_match_window, get_darts_playoff_process_match_window, \
    get_darts_playoff_choose_match_window
from handlers.judge.darts_menu.darts_qualifiers_windows import get_darts_team_choose_qualifiers_window, \
    get_darts_choose_player_qualifiers_window, \
    get_darts_get_score_qualifiers_window, get_darts_confirm_result_qualifiers_window, get_darts_history_window
from handlers.judge.kettle_manu.kettle_windows import get_kettle_team_choose_window, get_kettle_choose_lifter_window, \
    get_kettle_count_window, get_lifter_weight_window, get_kettle_confirm_result_window, get_kettle_history_window
from handlers.judge.main_windows import get_sports_window
from handlers.judge.football_menu.football_windows import get_matches_window, get_start_match_window, \
    get_process_window, \
    get_choose_scorer_window, get_finish_match_window, get_manual_match_create_window_1, \
    get_manual_match_create_window_2, get_red_card_choose_team_window, get_red_card_choose_player_window, \
    get_scorer_id_window, get_football_manual_set_group_window
from handlers.judge.pong_menu.pong_windows import get_pong_matches_window, get_pong_start_match_window, \
    get_pong_progress_window, get_pong_finish_set_window, get_pong_finish_match_window, \
    get_pong_manual_add_match_team_window_1, get_pong_manual_add_match_player_window_1, get_pong_manual_set_group_window
from handlers.judge.relay_menu.relay_windows import get_relay_team_choose, get_relay_confirm_result_window, \
    get_relay_time_register, get_relay_history_window
from handlers.judge.run_menu.run_windows import get_run_result_register_window, get_run_time_register_window, \
    get_run_confirm_result_window, get_run_history_window
from handlers.judge.tug_menu.tug_windows import get_tug_choose_match_window, get_tug_start_match_window, \
    get_tug_process_window, get_tug_finish_match_window, get_tug_manual_add_match_window_1, \
    get_tug_manual_add_match_window_2, get_tug_set_group_window
from handlers.judge.volleyball_menu.volleyball_windows import get_volleyball_matches_window, \
    get_volleyball_start_match_window, get_volleyball_process_window, get_volleyball_finish_set_window, \
    get_volleyball_manual_add_match_window_2, get_volleyball_manual_add_match_window_1, \
    get_volleyball_finish_match_window, get_volleyball_set_group_windows

dialog_router = Router()

football_dialog = Dialog(
    get_matches_window(),
    get_start_match_window(),
    get_process_window(),
    get_choose_scorer_window(),
    get_finish_match_window(),

    get_red_card_choose_team_window(),
    get_red_card_choose_player_window(),

    get_manual_match_create_window_1(),
    get_manual_match_create_window_2(),
    get_football_manual_set_group_window(),

    get_scorer_id_window()
)

volleyball_dialog = Dialog(
    get_volleyball_matches_window(),
    get_volleyball_start_match_window(),
    get_volleyball_process_window(),
    get_volleyball_manual_add_match_window_1(),
    get_volleyball_manual_add_match_window_2(),
    get_volleyball_set_group_windows(),

    get_volleyball_finish_match_window(),
    get_volleyball_finish_set_window()
)

pong_dialog = Dialog(
    get_pong_matches_window(),
    get_pong_start_match_window(),
    get_pong_progress_window(),
    get_pong_manual_add_match_team_window_1(),
    get_pong_manual_add_match_player_window_1(),
    get_pong_manual_set_group_window(),

    get_pong_finish_set_window(),
    get_pong_finish_match_window(),
)

run_dialog = Dialog(
    get_run_result_register_window(),
    get_run_time_register_window(),
    get_run_confirm_result_window(),
    get_run_history_window()
)

relay_dialog = Dialog(
    get_relay_team_choose(),
    get_relay_time_register(),
    get_relay_confirm_result_window(),

    get_relay_history_window()

)

tug_dialog = Dialog(
    get_tug_choose_match_window(),
    get_tug_start_match_window(),
    get_tug_process_window(),
    get_tug_finish_match_window(),

    get_tug_manual_add_match_window_1(),
    get_tug_manual_add_match_window_2(),
    get_tug_set_group_window()
)

kettle_dialog = Dialog(
    get_kettle_team_choose_window(),
    get_kettle_choose_lifter_window(),
    get_lifter_weight_window(),
    get_kettle_count_window(),
    get_kettle_confirm_result_window(),

    get_kettle_history_window()
)

darts_dialog = Dialog(
    get_darts_team_choose_qualifiers_window(),
    get_darts_choose_player_qualifiers_window(),
    get_darts_get_score_qualifiers_window(),
    get_darts_confirm_result_qualifiers_window(),

    get_darts_playoff_choose_first_player_window(),
    get_darts_playoff_choose_second_player_window(),
    get_darts_playoff_type_window(),
    get_darts_playoff_confirm_start_match_window(),
    get_darts_playoff_process_match_window(),

    get_darts_playoff_choose_match_window(),

    get_darts_history_window()
)

main_judge_dialog = Dialog(get_sports_window())

admin_dialog = Dialog(
    get_admin_start_window(),

    get_admin_choose_sport_to_fix_window(),
    get_admin_choose_team_to_fix_window(),
    get_admin_choose_match_to_fix_window(),
    get_admin_choose_goal_to_fix_window(),
    get_admin_fix_goal_approve_window(),

    get_create_groups_window(),
    get_create_groups_tournament_football_window(),
    get_create_groups_tournament_volleyball_window(),
    get_create_groups_tournament_pong_window(),
    get_choose_gender_pong_groups(),
    get_create_tug_tournament_groups_window(),

    get_admin_send_result_handler(),

    get_admin_add_judge_window()
)

dialog_router.include_router(main_judge_dialog)
dialog_router.include_router(football_dialog)
dialog_router.include_router(volleyball_dialog)
dialog_router.include_router(admin_dialog)
dialog_router.include_router(pong_dialog)
dialog_router.include_router(run_dialog)
dialog_router.include_router(tug_dialog)
dialog_router.include_router(relay_dialog)
dialog_router.include_router(kettle_dialog)
dialog_router.include_router(darts_dialog)
