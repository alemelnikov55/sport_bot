from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select

from api_requests.data_preparation_fonc import build_football_tournament_data, build_volleyball_tournament_data, \
    RunningResultBuilder, RelayResultBuilder, KettlebellResultBuilder, TugResultBuilder, DartsResultBuilder, \
    TableTennisResultBuilder
from api_requests.api_base_config import api

from database.football_requests import delete_goal, create_match
from database.pong_requests import create_pong_matches
from database.service_requests import add_judge
from database.tug_of_war_requests import create_tug_matches
from database.volleyball_requests import create_volleyball_matches
from handlers.admin.create_groups import distribute_teams_to_groups, generate_group_matches
from handlers.judge.state import AdminStates

SPORTS = {'football': AdminStates.football_choose_team_to_fix}


async def fix_score_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.choose_sport_to_fix)
    await call.answer('Корректировка счета')


async def create_groups_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.create_groups)
    await call.answer('Создание групп')


async def create_football_tournament_groups(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['sport_name'] = 'Мини-футбол'
    await dialog_manager.switch_to(AdminStates.create_football_tournament_groups)
    await call.answer('Создание групп для футбола')


async def create_volleyball_tournament_groups(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['sport_name'] = 'Волейбол'
    await dialog_manager.switch_to(AdminStates.create_volleyball_tournament_groups)
    await call.answer('Создание групп для волейбола')


async def create_pong_tournament_groups(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['sport_name'] = 'Настольный теннис'
    await dialog_manager.switch_to(AdminStates.choose_gender_pong)
    await call.answer('Создание групп для пинг-понга')


async def create_tug_tournament_groups(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['sport_name'] = 'Перетягивание каната'
    await dialog_manager.switch_to(AdminStates.create_tug_tournament_groups)
    await call.answer('Создание групп для перетягивания каната')


async def pong_choose_gender_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    gender = button.widget_id.split('_')[-1]
    dialog_manager.dialog_data['pong_gender'] = gender

    await dialog_manager.switch_to(AdminStates.create_pong_tournament_groups)
    await call.answer('Группа выбрана')


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

    # Отправка данных о турнирной сетке футбольного турнира в API
    tournament_data = await build_football_tournament_data(session)
    api.send_tournament_stages(tournament_data)
    print(tournament_data)

    await message.answer(f'Создано групповых матчей по футболу: {matches_count}')
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

    matches_count = sum(len(matches) for matches in groups_matches.values())

    # очистка данных из данных диалога
    del dialog_manager.dialog_data['teams_for_groups']
    del dialog_manager.dialog_data['teams_count']

    # Отправка данных о турнирной сетке турнира по волейболу в API
    tournament_data = await build_volleyball_tournament_data(session)
    api.send_tournament_stages(tournament_data)
    print(tournament_data)

    await message.answer(f'Создано групповых матчей по волейболу: {matches_count}')
    await dialog_manager.switch_to(AdminStates.start_menu)


async def groups_pong_count_inpout_handler(message: Message, message_inpout: MessageInput,
                                           dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    expected_total = dialog_manager.dialog_data['player_count']
    players = dialog_manager.dialog_data['player_for_groups']
    players_amount_array = list(map(int, message.text.split()))
    teams_amount_sum = sum(players_amount_array)

    # Проверка: только цифры через пробел
    if not all(part.isdigit() for part in message.text.split()):
        await message.answer('Пожалуйста, введите только числа, разделённые пробелами.')
        return

    if teams_amount_sum != expected_total:
        await message.answer(f"Сумма чисел должна быть равна {expected_total}. Попробуйте снова.")
        return

    # Подготовка групп для матчей
    groups_array = distribute_teams_to_groups(players, players_amount_array)
    groups_matches = generate_group_matches(groups_array)

    await create_pong_matches(session, groups_matches)

    matches_count = sum(len(matches) for matches in groups_matches.values())

    # очистка данных из данных диалога
    del dialog_manager.dialog_data['player_for_groups']
    del dialog_manager.dialog_data['player_count']

    await message.answer(f'Создано групповых матчей по настольному теннису: {matches_count}')
    await dialog_manager.start(AdminStates.start_menu)


async def groups_tug_count_inpout_handler(message: Message, message_inpout: MessageInput,
                                          dialog_manager: DialogManager):
    session = dialog_manager.middleware_data['session']
    expected_total = dialog_manager.dialog_data['tug_teams_count']
    players = dialog_manager.dialog_data['tug_teams_for_groups']
    players_amount_array = list(map(int, message.text.split()))
    teams_amount_sum = sum(players_amount_array)

    # Проверка: только цифры через пробел
    if not all(part.isdigit() for part in message.text.split()):
        await message.answer('Пожалуйста, введите только числа, разделённые пробелами.')
        return

    if teams_amount_sum != expected_total:
        await message.answer(f"Сумма чисел должна быть равна {expected_total}. Попробуйте снова.")
        return

    # Подготовка групп для матчей
    groups_array = distribute_teams_to_groups(players, players_amount_array)
    groups_matches = generate_group_matches(groups_array)

    await create_tug_matches(session, groups_matches)

    matches_count = sum(len(matches) for matches in groups_matches.values())

    # очистка данных из данных диалога
    del dialog_manager.dialog_data['tug_teams_count']
    del dialog_manager.dialog_data['tug_teams_for_groups']

    await message.answer(f'Создано групповых матчей по перетягиванияю каната: {matches_count}')
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


async def admin_send_result_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(AdminStates.send_result)
    await call.answer('Отправка результатов')


async def send_result_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    sport = button.widget_id.split('_')[1]
    session = dialog_manager.middleware_data['session']
    if sport == 'run':
        for distance in (100, 2000, 3000):
            result_builder = RunningResultBuilder(session, distance)
            api.send_results(await result_builder.build())
            print(await result_builder.build())
    await call.answer('Отправка результатов')

    if sport == 'relay':
        result_builder = RelayResultBuilder(session)
        api.send_results(await result_builder.build())
        print(await result_builder.build())

    if sport == 'kettle':
        builder = KettlebellResultBuilder(session)
        kettle_result = await builder.build()
        api.send_results(kettle_result)

    if sport == 'tug':
        # TODO выставить число команд в плей-офф
        builder = TugResultBuilder(session)
        tug_result = await builder.build(4)
        api.send_results(tug_result)

    if sport == 'darts':
        builder = DartsResultBuilder(session)
        darts_result = await builder.build()
        api.send_results(darts_result)

    if sport == 'pong':
        builder = TableTennisResultBuilder(session)
        pong_result = await builder.build()
        api.send_results(pong_result)

    await call.message.answer(f'Результаты {sport} отправлены')

    await call.answer('Результаты отправлены')


async def back_to_panel_handler(call: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start_menu)
    await call.answer('Назад!')
