# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery
#
# from database.football_requests import create_match
#
#
# async def admin_callback_handler(call: CallbackQuery, state: FSMContext):
#     call_data = call.data.split('_')
#     state_data = await state.get_data()
#     groups_matches = state_data.get('groups_matches')
#     if groups_matches is None:
#         return
#
#     matches_count = 0
#     formated_groups = ' '.join([group for group, matches in groups_matches.items()])
#
#     if call_data[1] == 'confirmGroups':
#         for group, matches in groups_matches.items():
#             for math_pair in matches:
#                 team_1, team_2 = math_pair
#                 await create_match(team_1, team_2, group)
#                 matches_count += 1
#
#     await call.message.delete_reply_markup()
#     await call.answer(f'Было создано {matches_count} матчей в группах {formated_groups}')
#     await call.message.answer(f'Было создано {matches_count} матчей в группах {formated_groups}')