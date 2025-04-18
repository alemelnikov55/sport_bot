from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.api.protocols import MessageNotModified
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select

from database.football_requests import delete_goal, create_match
from database.service_requests import add_judge
from database.volleyball_requests import create_volleyball_matches
from handlers.admin.create_football_group import distribute_teams_to_groups, generate_group_matches
from handlers.judge.state import AdminStates

SPORTS = {'football': AdminStates.football_choose_team_to_fix}


async def fix_score_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.choose_sport_to_fix)
    await call.answer('Корректировка счета')


async def create_groups_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.create_groups)
    await call.answer('Создание групп')


async def create_football_tournament_groups(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.create_football_tournament_groups)
    await call.answer('Создание групп для футбола')


async def create_volleyball_tournament_groups(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.create_volleyball_tournament_groups)
    await call.answer('Создание групп для волейбола')


async def choose_sport_to_fix_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager,
                                      sport_id: str):
    dialog_manager.dialog_data['sport_to_fix'] = sport_id
    await dialog_manager.switch_to(SPORTS[sport_id])
    await call.answer('Выбран спорт')


async def choose_team_to_fix_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, team_id: str):
    dialog_manager.dialog_data['team_to_fix'] = team_id
    await dialog_manager.next()


async def choose_match_to_fix_handler(call: CallbackQuery, button: Select, dialog_manager: DialogManager,
                                      match_id: str):
    dialog_manager.dialog_data['match_to_fix'] = match_id
    await dialog_manager.switch_to(AdminStates.football_choose_goal_to_fix)
    await call.answer('Выбран матч')


async def choose_goal_to_fix_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager, goal_id: str):
    dialog_manager.dialog_data['goal_to_fix'] = goal_id
    await dialog_manager.next()
    await call.answer('Выбран гол')


async def admin_fix_goal_approve_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    goal_id = int(dialog_manager.dialog_data['goal_to_fix'])
    team_id = int(dialog_manager.dialog_data['team_to_fix'])
    match_id = int(dialog_manager.dialog_data['match_to_fix'])

    await delete_goal(session, match_id, goal_id, team_id)

    await dialog_manager.switch_to(AdminStates.start_menu)
    await call.answer('Гол удален')


async def admin_fix_goal_refuse_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.start_menu)
    await call.answer('Отмена удаления')


async def back_admin_choose_goal_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def back_admin_choose_match_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def back_admin_choose_team_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def back_admin_choose_sport_to_fix(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def groups_football_count_inpout_handler(message: Message, message_inpout: MessageInput,
                                               dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']

    expected_total = dialog_manager.dialog_data['teams_count']
    teams = dialog_manager.dialog_data['teams_for_groups']
    teams_amount_array = list(map(int, message.text.split()))
    teams_amount_sum = sum(teams_amount_array)
    matches_count = 0

    # Проверка: только цифры через пробел
    if not all(part.isdigit() for part in message.text.split()):
        await message.answer('Пожалуйста, введите только числа, разделённые пробелами.')
        return

    if teams_amount_sum != expected_total:
        await message.answer(f"Сумма чисел должна быть равна {expected_total}. Попробуйте снова.")
        return

    groups_array = distribute_teams_to_groups(teams, teams_amount_array)

    groups_matches = generate_group_matches(groups_array)

    for group, matches in groups_matches.items():
        for math_pair in matches:
            team_1, team_2 = math_pair
            await create_match(session, team_1, team_2, group)
            matches_count += 1

    # очистка данных из данных диалога
    del dialog_manager.dialog_data['teams_for_groups']
    del dialog_manager.dialog_data['teams_count']

    await message.answer(f'Создано групповых матчей: {matches_count}')
    await dialog_manager.switch_to(AdminStates.start_menu)


# TODO эта и предыдущая функции - почти копии. Обдумать как объединить
async def groups_volleyball_count_inpout_handler(message: Message, message_inpout: MessageInput,
                                                 dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    expected_total = dialog_manager.dialog_data['teams_count']
    teams = dialog_manager.dialog_data['teams_for_groups']
    teams_amount_array = list(map(int, message.text.split()))
    teams_amount_sum = sum(teams_amount_array)

    # Проверка: только цифры через пробел
    if not all(part.isdigit() for part in message.text.split()):
        await message.answer('Пожалуйста, введите только числа, разделённые пробелами.')
        return

    if teams_amount_sum != expected_total:
        await message.answer(f"Сумма чисел должна быть равна {expected_total}. Попробуйте снова.")
        return

    groups_array = distribute_teams_to_groups(teams, teams_amount_array)

    groups_matches = generate_group_matches(groups_array)
    await create_volleyball_matches(session, groups_matches)
    print(groups_matches)
    matches_count = sum(len(matches) for matches in groups_matches.values())

    # очистка данных из данных диалога
    del dialog_manager.dialog_data['teams_for_groups']
    del dialog_manager.dialog_data['teams_count']

    await message.answer(f'Создано групповых матчей: {matches_count}')
    await dialog_manager.switch_to(AdminStates.start_menu)


async def add_judge_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.add_judge)
    await call.answer('Добавление судей')


async def add_judge_inpout_handler(message: Message, message_inpout: MessageInput, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    bot: Bot = dialog_manager.middleware_data['bot']
    text = message.text

    if not text.isdigit():
        await message.answer('Пожалуйста, введите только id пользователя.')
        return

    try:
        await bot.send_message(text, 'Вам добавлена роль судьи')
    except TelegramBadRequest:
        await message.answer('Не удалось добавить судью, проверьте правильность ввода id.')
        return

    await add_judge(session, int(text))

    await dialog_manager.switch_to(AdminStates.start_menu)
    await message.answer(f'Судья добавлен')
