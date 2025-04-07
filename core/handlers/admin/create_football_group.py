from itertools import combinations
from typing import List, Dict

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.service_requests import get_teams_by_sport
from utils.states import GroupCreationStates

GROUPS_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


async def create_football_group(message: Message, state: FSMContext, session: AsyncSession):
    """Создание футбольных групп для турнира

    по заданным параметрам от администратора формирует Группы и матчи Все со Всеми в рамках группы
    """
    teams = await get_teams_by_sport('football', session)
    teams_amount = len(teams)

    await state.update_data(teams_amount=teams_amount, teams=teams)
    await state.set_state(GroupCreationStates.get_teams_amount)

    await message.answer(f'Зарегистрировано {teams_amount} команд. Через пробел введите количество участников в группе')


async def get_teams_amount(message: Message, state: FSMContext, session: AsyncSession):
    """Получение и обработка числа команд в группе"""
    teams_amount_array = [int(num) for num in message.text.split(' ')]
    teams_amount_sum = sum(teams_amount_array)

    data = await state.get_data()
    teams_amount = data.get('teams_amount')

    if teams_amount_sum != teams_amount:
        await message.answer(f'Сумма всех групп не равна количеству команд! Попробуйте еще раз.')
        return

    teams = data.get('teams')
    groups_array = distribute_teams_to_groups(teams, teams_amount_array)
    print(groups_array)

    groups_matches = generate_group_matches(groups_array)
    print(groups_matches)
    await state.update_data(groups_matches=groups_matches)
    formated_matches = format_matches_for_referees(groups_matches, teams)

    answer_text = f'Расписание групповых матчей:\n{formated_matches}'

    await message.answer(answer_text, reply_markup=confirm_groups_keyboard())


def distribute_teams_to_groups(teams_dict, group_sizes):
    """
    Распределяет команды по группам на основе их индексов.

    :param teams_dict: словарь {название_команды: индекс_команды}
    :param group_sizes: список с количеством команд в каждой группе
    :return: словарь {название_группы: [индексы_команд]}
    """
    team_indices = [idx for name, idx in teams_dict.items()]

    result = {}
    start = 0

    for i, size in enumerate(group_sizes):
        group_name = GROUPS_LETTERS[i]
        end = start + size
        result[group_name] = team_indices[start:end]
        start = end

    return result


def generate_group_matches(grouped_teams):
    """
    Генерирует матчи внутри каждой группы по принципу "каждый с каждым"

    :param grouped_teams: словарь {название_группы: [индексы_команд]}
    :return: словарь {название_группы: [(индекс1, индекс2), ...]}
    """
    group_matches = {}

    for group_name, teams in grouped_teams.items():
        # Генерируем все уникальные пары команд в группе
        matches = list(combinations(teams, 2))
        group_matches[group_name] = matches

    return group_matches


def format_matches_for_referees(group_matches, teams_dict):
    """
    Форматирует список матчей для отправки судьям с названиями команд

    :param group_matches: результат generate_group_matches()
                         {группа: [(id1, id2), ...]}
    :param teams_dict: словарь {название_команды: id_команды}
    :return: текстовый формат для отправки судьям
    """
    # Создаем обратный словарь {id: название_команды}
    id_to_team = {v: k for k, v in teams_dict.items()}

    output_text = ''

    for group_name, matches in group_matches.items():
        output_text += f"=== Группа {group_name} ===\n"

        for i, (team1_id, team2_id) in enumerate(matches, 1):
            team1 = id_to_team.get(team1_id, f"Команда {team1_id}")
            team2 = id_to_team.get(team2_id, f"Команда {team2_id}")
            output_text += f"Матч {i}: {team1} vs {team2}\n"

        output_text += "\n"  # Пустая строка между группами

    return output_text


def confirm_groups_keyboard() -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()

    kb_builder.button(text='Подтвердить', callback_data='a_confirmGroups')

    return kb_builder.as_markup()
