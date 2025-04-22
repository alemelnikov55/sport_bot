"""
Модель обработки callback от судей
модель callback от судей:
j_<sport_id>_<entity_id>_<action>_<доп информация>
0     1          2          3            4
для всех - "-" не актуально
2: m - match - вы бор матча
   s - sport - выбор спорта
   t - team
3: c - choose
   s - start
   f - finish
   g - goal
   p - choose participant

"""
from pprint import pprint

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import get_active_matches, get_match_teams_info, change_match_status, add_goal
from database.models import MatchStatus
from database.service_requests import get_team_participants_by_team_and_sport


def transform_match_data(matches_dict):
    """
    Преобразует словарь матчей в формат {"match_id": "team1 :: team2"}

    :param matches_dict: Словарь с матчами по группам
    :return: Словарь с ключами match_id (str) и значениями "team1 :: team2"
    """
    transformed_data = {}

    for group, matches in matches_dict.items():
        for match in matches:
            match_id = str(match['match_id'])
            transformed_data[match_id] = f"{match['team1']} :: {match['team2']}"

    return transformed_data


def create_judge_callback_text(old_sport, old_entity, old_action, addition) -> str:
    """
    Создает текст для кнопки выбора судейства
    :param old_sport: Старое значение спорта
    :param old_entity: Старое значение сущности
    :param old_action: Старое значение действия
    :param addition: Старое значение id
    """
    return f'j_{old_sport}_{old_entity}_{old_action}_{addition}'


async def judge_callback_handler(callback: CallbackQuery, state: FSMContext, bot: Bot, session: AsyncSession):
    """Обработка нажатий на клавиатуру от судей"""
    data = callback.data.split('_')
    print(data)
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    # TODO sport_id зависим от индекса спорта в базе данных
    sport_id = data[1]  # id спорта
    entity_id = data[2]  # id сущности (вид спорта, лига, турнир, матчи)
    action = data[3]  # действие, выбранное пользователем
    # вид спорта уже выбрали
    if sport_id == '5':  # если это футбол
        # j_{sport_id}_m_c_-
        print('football')
        # Для выбора матча
        if entity_id == 's' and action == 'c':
            print('выбираем матч')
            matches = await get_active_matches()

            await state.update_data(matches=matches, sport_id=sport_id)

            await bot.edit_message_text('Выберите матч для судейства:',
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=choose_football_match_kb(matches, sport_id))

        # если выбрана команда
        if entity_id == 'm' and action == 'c':
            print('запуска матч')
            match_id = int(data[4])
            match_info = await get_match_teams_info(session, match_id)
            formatted_match_info = (f'{match_info["team1"]["name"]} :: {match_info["team2"]["name"]}\n'
                                    f'Группа: {match_info["group"]}')
            await bot.edit_message_text(f'Был выбран матч: {formatted_match_info}',
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=activate_chosen_match_kb(sport_id, entity_id, action, match_id))

        # запускаем матч
        if entity_id == 'm' and action == 's':
            match_id = int(data[4])
            await change_match_status(match_id, MatchStatus.IN_PROGRESS, session)
            match_info = await get_match_teams_info(session, match_id)
            print(match_info)
            team_1 = match_info['team1']
            team_2 = match_info['team2']
            await state.clear()

            await state.update_data(team_1=team_1, team_2=team_2)

            await bot.edit_message_text(f'группа: {match_info["group"]}\n{team_1["name"]} 0 : 0 {team_2["name"]}\n',
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=await football_goal_add_kb(match_id, team_1, team_2))

        # забили гол
        if entity_id == 'm' and action == 'g':
            """j_5_m_g_{team_1["id"]}_m{match}"""
            print('забили гол')

            match_id = int(data[5][1:])
            team_id = int(data[4])

            text = callback.message.text
            await state.update_data(text=text)

            await bot.edit_message_text('Выбери автора гола:',
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=await football_choose_goal_participant_kb(match_id,
                                                                                               team_id,
                                                                                               session))

        # выбрали автора гола
        if entity_id == 'm' and action == 'p':
            """ f'j_5_ m_g_m{match}_p{id_}'"""
            match_id = int(data[4][1:])
            participant_id = int(data[5][1:])

            data = await state.get_data()
            old_text = data['text']
            team_1 = data['team_1']
            team_2 = data['team_2']

            pprint(data)

            await add_goal(match_id, participant_id)

            await bot.edit_message_text(text=old_text + f'гол от {participant_id}',
                                           chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=await football_goal_add_kb(match_id, team_1, team_2))

        # кнопка Назад если не тот матч
        if entity_id == 'm' and action == 'b':
            print('Назад')
            data = await state.get_data()
            matches = data['matches']
            sport_id = data['sport_id']
            await bot.edit_message_text(f'Выберите матч для судейства:',
                                        chat_id=chat_id,
                                        message_id=message_id,
                                        reply_markup=choose_football_match_kb(matches, sport_id))

    await callback.answer(text='выбор сделан')


def choose_football_match_kb(matches_dict, sport_id: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками выбора матчей по футболу

    :param matches_dict:
    :param sport_id: id спорта, по которому создаются кнопки
    :return:
    """
    transformed_data = transform_match_data(matches_dict)
    kb_builder = InlineKeyboardBuilder()

    for match_id, match_data in transformed_data.items():
        kb_builder.button(text=match_data, callback_data=f'j_{sport_id}_m_c_{match_id}')

    # kb_builder.button(text='Ручной ввод', callback_data='j_m_manual')
    kb_builder.row(InlineKeyboardButton(text='Ручной ввод', callback_data='j_m_manual'))
    kb_builder.adjust(1)

    return kb_builder.as_markup()


def activate_chosen_match_kb(sport: str, entity: str, action: str, match: int) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры для активации выбранного матча

    :param sport
    :param entity
    :param action
    :param match
    :return:
    """
    kb_builder = InlineKeyboardBuilder()
    # old_callback = create_judge_callback_text(sport, entity, action, match)

    kb_builder.button(text='Начать матч', callback_data=f'j_{sport}_{entity}_s_{match}')
    kb_builder.button(text='Назад', callback_data=f'j_{sport}_m_b')

    return kb_builder.as_markup()


async def football_goal_add_kb(match: int, team_1: dict, team_2: dict) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора команды которая забила гол

    :param match:
    :param team_1:
    :param team_2:
    :return:
    """
    kb_builder = InlineKeyboardBuilder()
    """await add_goal(match_id, user_id)"""

    kb_builder.row(InlineKeyboardButton(text=team_1['name'], callback_data=f'j_5_m_g_{team_1["id"]}_m{match}'),
                   InlineKeyboardButton(text=team_2['name'], callback_data=f'j_5_m_g_{team_2["id"]}_m{match}'), width=2)

    kb_builder.row(InlineKeyboardButton(text='Завершить матч', callback_data=f'j_5_m_f_{match}'))

    return kb_builder.as_markup()


async def football_choose_goal_participant_kb(match: int, team: int, session: AsyncSession) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    print('Goal!')
    print(f'{match} - {team}')
    participants = await get_team_participants_by_team_and_sport(team, 'football', session)
    for name, id_ in participants.items():
        print(f'{name} - {id_}')
        kb_builder.button(text=f'{name.split(" ")[0]} {id_}', callback_data=f'j_5_m_p_m{match}_p{id_}')

    # обдумать callback
    kb_builder.button(text='Ручной ввод', callback_data=f'j_5_m_p_m{match}_manual')
    kb_builder.button(text='Назад', callback_data=f'j_5_m_p_m{match}_back')

    kb_builder.adjust(1)

    return kb_builder.as_markup()
