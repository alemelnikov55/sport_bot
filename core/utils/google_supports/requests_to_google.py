import os
from pathlib import Path

import gspread
from typing import List, Dict, Union

from oauth2client.service_account import ServiceAccountCredentials
from gspread.utils import ValueRenderOption
from gspread.exceptions import WorksheetNotFound

from core.utils.data_converters import transform_participants, transform_participant

missing_counter = {"count": 0}

TABLE_NAME = 'bot_test'

abs_path = Path(os.path.dirname(__file__))

# Укажите область доступа
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Замените 'path/to/your/service_account.json' на путь к вашему JSON-файлу
creds = ServiceAccountCredentials.from_json_keyfile_name(f'{abs_path}/credentials.json', scope)

# Подключение к Google Sheets
client = gspread.authorize(creds)

# Откройте таблицу по названию
spreadsheet = client.open(TABLE_NAME)


def get_filtered_participants_data(sheet_name: str) -> List[Dict[str, Union[int, str, None, List[str]]]]:
    """
    Получает данные участников из таблицы Google Sheets с фильтрацией и преобразует виды спорта в список

    :param sheet_name: Название листа
    :return: Список словарей с данными участников, где виды спорта собраны в список
    """
    # Столбцы, которые нужно исключить
    EXCLUDED_COLUMNS = {"Справка", "Цвет манишки", "Комментарий"}

    # Полные названия колонок, которые содержат информацию о видах спорта
    SPORTS_COLUMNS_FULL = {
        "football",
        "volleyball",
        "run_100m",
        "run_1000m",
        "relay_race_4x100",
        "cheerleading",
        "relay_race_in_sacks",
        "tug_of_war"
    }

    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except WorksheetNotFound as exc:
        print(f"Лист '{sheet_name}' не найден: {exc}")
        raise exc

    # Получаем все данные
    raw_data = worksheet.get_all_values(value_render_option=ValueRenderOption.formula)

    if not raw_data:
        print(f"Лист '{sheet_name}' пуст")
        return []

    # Заголовки столбцов
    headers = [str(header).strip() for header in raw_data[0]]

    result = []

    for row in raw_data[1:]:
        row_dict = {}
        sports_list = []

        for i, (header, value) in enumerate(zip(headers, row)):
            # Пропускаем исключенные столбцы
            if header in EXCLUDED_COLUMNS:
                continue

            # Пропускаем пустые значения
            if not value or str(value).strip() == "":
                continue
            sport_name = header.split()[0]
            # Проверяем, является ли столбец видом спорта
            if sport_name in SPORTS_COLUMNS_FULL:
                if str(value).strip().lower() in ["да", "yes", "+", "1"]:
                    # Берем только первое слово из названия вида спорта

                    sports_list.append(sport_name)
                continue

            # Обработка обычных значений
            processed_value = value.strip() if isinstance(value, str) else value

            # Добавляем только непустые значения
            if processed_value is not None and processed_value != "":
                row_dict[header] = processed_value

        # Добавляем список видов спорта
        if sports_list:
            row_dict["sports"] = sports_list

        # Добавляем только строки с данными, исключая строку "Итог"
        if row_dict and row_dict.get('ФИО участника') != 'Итог':
            result.append(row_dict)

    print(f"Получено {len(result)} отфильтрованных записей участников")
    result = transform_participants(result, missing_counter)
    return result


def update_google_sheet(data: dict):
    """
    Фнкция обновления таблицы в Google Sheets

    полностью перезаписывает данные в листе, создает лист, если его нет
    :param data:
    :return:
    """

    for sport, groups in data.items():
        try:
            worksheet = client.open(TABLE_NAME).worksheet(sport)
        except gspread.exceptions.WorksheetNotFound:
            worksheet = client.open(TABLE_NAME).add_worksheet(title=sport, rows=100, cols=10)

        # Очистка листа перед записью новых данных
        worksheet.clear()

        # Заголовки таблицы
        headers = ["Группа", "Команда 1", "Голы 1", "Голы 2", "Команда 2", "Игроки (Команда 1)", "Игроки (Команда 2)"]
        worksheet.append_row(headers)

        rows = []
        for group, matches in groups.items():
            for match in matches:
                team_1 = match['team_1']
                team_2 = match['team_2']
                players_1 = ', '.join([f"{p[0]} ({p[1]})" for p in team_1['players']]) if team_1['players'] else "-"
                players_2 = ', '.join([f"{p[0]} ({p[1]})" for p in team_2['players']]) if team_2['players'] else "-"

                row = [group, team_1['name'], team_1['goals'], team_2['goals'], team_2['name'], players_1, players_2]
                rows.append(row)

        # Записываем все строки разом
        worksheet.append_rows(rows)


# print(get_filtered_participants_data('123'))

# update_google_sheet({'football': {'1/2': [{'team_1': {'goals': 0,
#                                   'match_id': 5,
#                                   'name': 'ШК и корпслужбы',
#                                   'players': []},
#                        'team_2': {'goals': 1,
#                                   'match_id': 5,
#                                   'name': 'ОК Казахстан',
#                                   'players': [('Билан', 40)]}},
#                       {'team_1': {'goals': 0,
#                                   'match_id': 6,
#                                   'name': 'ШК и корпслужбы',
#                                   'players': []},
#                        'team_2': {'goals': 1,
#                                   'match_id': 6,
#                                   'name': 'ОК Казахстан',
#                                   'players': [('Билан', 40)]}},
#                       {'team_1': {'goals': 0,
#                                   'match_id': 10,
#                                   'name': 'ШК и корпслужбы',
#                                   'players': []},
#                        'team_2': {'goals': 1,
#                                   'match_id': 10,
#                                   'name': 'ОК Казахстан',
#                                   'players': [('Билан', 40)]}},
#                       {'team_1': {'goals': 0,
#                                   'match_id': 11,
#                                   'name': 'ШК и корпслужбы',
#                                   'players': []},
#                        'team_2': {'goals': 1,
#                                   'match_id': 11,
#                                   'name': 'ОК Казахстан',
#                                   'players': [('Билан', 40)]}}],
#               'A': [{'team_1': {'goals': 0,
#                                 'match_id': 1,
#                                 'name': 'ОК Волга-Дон',
#                                 'players': []},
#                      'team_2': {'goals': 2,
#                                 'match_id': 1,
#                                 'name': 'КСЦ',
#                                 'players': [('Билан', 40), ('Билан', 40)]}},
#                     {'team_1': {'goals': 2,
#                                 'match_id': 2,
#                                 'name': 'ОК БиС',
#                                 'players': [('Билан', 40), ('Билан', 40)]},
#                      'team_2': {'goals': 0,
#                                 'match_id': 2,
#                                 'name': 'ППК Шторм',
#                                 'players': []}},
#                     {'team_1': {'goals': 2,
#                                 'match_id': 7,
#                                 'name': 'ОК БиС',
#                                 'players': [('Билан', 40), ('Билан', 40)]},
#                      'team_2': {'goals': 0,
#                                 'match_id': 7,
#                                 'name': 'ППК Шторм',
#                                 'players': []}}],
#               'B': [{'team_1': {'goals': 1,
#                                 'match_id': 3,
#                                 'name': 'ОК БиС',
#                                 'players': [('Билан', 40)]},
#                      'team_2': {'goals': 0,
#                                 'match_id': 3,
#                                 'name': 'ППК Шторм',
#                                 'players': []}},
#                     {'team_1': {'goals': 0,
#                                 'match_id': 4,
#                                 'name': 'ОК БиС',
#                                 'players': []},
#                      'team_2': {'goals': 0,
#                                 'match_id': 4,
#                                 'name': 'ППК Шторм',
#                                 'players': []}},
#                     {'team_1': {'goals': 1,
#                                 'match_id': 8,
#                                 'name': 'ОК БиС',
#                                 'players': [('Билан', 40)]},
#                      'team_2': {'goals': 0,
#                                 'match_id': 8,
#                                 'name': 'ППК Шторм',
#                                 'players': []}},
#                     {'team_1': {'goals': 0,
#                                 'match_id': 9,
#                                 'name': 'ОК БиС',
#                                 'players': []},
#                      'team_2': {'goals': 0,
#                                 'match_id': 9,
#                                 'name': 'ППК Шторм',
#                                 'players': []}}]}})
