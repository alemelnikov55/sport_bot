import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import logging

import gspread
from typing import List, Dict, Union, Any, Callable

from oauth2client.service_account import ServiceAccountCredentials
from gspread.utils import ValueRenderOption
from gspread.exceptions import WorksheetNotFound

from utils.data_converters import transform_participants
from handlers.judge.run_menu.run_handlers import format_seconds_to_time_string

logger = logging.getLogger(__name__)

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

# === Регистрация обработчиков по листам ===
sheet_handlers: Dict[str, Callable[[Any], list]] = {}

# Столбцы, которые нужно исключить
EXCLUDED_COLUMNS = {"Справка", "Цвет манишки", "Комментарий"}

# Полные названия колонок, которые содержат информацию о видах спорта
SPORTS_COLUMNS_FULL = {
    "football",
    "volleyball",
    "run_100m",
    "run_2000m",
    "run_3000m",
    "relay_race_4x100",
    "pong",
    "tug_of_war",
    'kettle',
    'darts'
}


def get_filtered_participants_data(sheet_name: str) -> List[Dict[str, Union[int, str, None, List[str]]]]:
    """
    Получает данные участников из таблицы Google Sheets с фильтрацией и преобразует виды спорта в список

    :param sheet_name: Название листа
    :return: Список словарей с данными участников, где виды спорта собраны в список
    """
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

    logger.info(f"Получено {len(result)} отфильтрованных записей участников")
    result = transform_participants(result, missing_counter)
    return result


def register_sheet_handler(sheet_name: str):
    def wrapper(func):
        sheet_handlers[sheet_name] = func
        return func

    return wrapper


# === Пример обработчика для листа volleyball_results ===
@register_sheet_handler("football")
def handle_football(data):
    headers = ["Группа", "Команда 1", "Голы 1", "Голы 2", "Команда 2", "Игроки (Команда 1)", "Игроки (Команда 2)", 'Красные карточки']
    rows = [headers]

    for group, matches in data.items():
        for match in matches:
            team_1 = match['team_1']
            team_2 = match['team_2']
            red_cards = match['red_cards']

            players_1 = ', '.join([f"{p[0]} ({p[1]})" for p in team_1['players']]) if team_1['players'] else "-"
            players_2 = ', '.join([f"{p[0]} ({p[1]})" for p in team_2['players']]) if team_2['players'] else "-"

            red_cards = ', '.join([f"{p[0]} ({p[1]})" for p in red_cards]) if red_cards else "-"

            row = [group, team_1['name'], team_1['goals'], team_2['goals'], team_2['name'], players_1, players_2, red_cards]
            rows.append(row)

    return rows


@register_sheet_handler("volleyball")
def handle_volleyball(data):
    """
    Форматирует данные волейбольных матчей для вставки в Google Sheet.
    :param data: Словарь матчей по группам
    :return: Табличные данные со строками
    """
    headers = ["Группа", "Команда 1", "Счёт по сетам", "Счёт по сетам", "Команда 2", "Сеты"]
    rows = [headers]

    for group, matches in data.items():
        for match in matches:
            team1 = match['team1']
            team2 = match['team2']

            # Счёт по сетам
            sets_team1 = team1['sets_won']
            sets_team2 = team2['sets_won']

            # Очки по сетам
            set_scores = []
            for s1, s2 in zip(team1['scores'], team2['scores']):
                set_scores.append(f"{s1['score']} - {s2['score']}")

            row = [
                group,
                team1['name'],
                sets_team1,
                sets_team2,
                team2['name'],
                ", ".join(set_scores)
            ]
            rows.append(row)

    return rows


@register_sheet_handler('pong')
def handle_pong(data):
    headers = ["Группа", "Игрок 1", "Счёт по сетам", "Счёт по сетам", "Игрок 2", "Сеты"]
    rows = [headers]

    for group, matches in data.items():
        for match in matches:
            player1 = match['player1']
            player2 = match['player2']

            # Счёт по сетам
            sets_player1 = player1['sets_won']
            sets_player2 = player2['sets_won']

            # Очки по сетам
            set_scores = []
            for set_ in match['sets']:
                set_scores.append(f"{set_['player1_score']} - {set_['player2_score']}")

            row = [
                group,
                player1['name'],
                sets_player1,
                sets_player2,
                player2['name'],
                ", ".join(set_scores)
            ]
            rows.append(row)

    return rows


@register_sheet_handler('run_3000')
@register_sheet_handler('run_2000')
@register_sheet_handler('run_100')
def handle_run(data):
    headers = ['№', 'ФИО', 'Команда', 'Время, с']
    rows = [headers]

    # try:
    if data is not None:
        for result in data:
            row = [
                result['participant_id'],
                result['full_name'],
                result['team_name'],
                format_seconds_to_time_string(result['result_time'])
            ]

            rows.append(row)
    # except Exception as e:
    #     logger.exception(f"Error: {e}")

    return rows


@register_sheet_handler('relay')
def handle_relay(data):
    headers = ['Команда', 'Время, с']
    rows = [headers]

    if data is not None:
        for result in data:
            row = [
                result['team_name'],
                format_seconds_to_time_string(result['result_time'])
            ]
            rows.append(row)

    return rows


@register_sheet_handler('tug')
def handle_tug(data):
    headers = ['Группа', 'Команда 1', 'Победы 1', 'Победы 2', 'Команда 2']
    rows = [headers]

    for group, matches in data.items():
        for match in matches:
            team1_name = match['team1']['name']
            team2_name = match['team2']['name']

            team1_score = match['team1']['score']
            team2_score = match['team2']['score']

            row = [
                group,
                team1_name,
                team1_score,
                team2_score,
                team2_name,
            ]
            rows.append(row)

    return rows


@register_sheet_handler('kettle')
def handle_kettle(data):
    headers = ['Пол', 'Категория', 'Возраст', 'ФИО', 'Команда', 'Результат']
    rows = [headers]

    for result in data:
        if result['weight'] <= 73:
            weight_category = "до 73 кг"
        elif result['weight'] <= 85:
            weight_category = "до 85 кг"
        else:
            weight_category = "свыше 85 кг"
        row = [
            result['gender'],
            result['weight'] if result['gender'] == 'F' else weight_category,
            result['age'] if result['gender'] == 'F' else "18-34" if result['age'] < 35 else "35+",
            result['full_name'],
            result['team_name'],
            result['lift_count']
        ]
        rows.append(row)

    return rows


@register_sheet_handler('darts_qualifiers')
def handle_darts_qualifiers(data):
    headers = ('Команда', 'Игрок', 'Набрано очков')
    rows = [headers]

    for result in data:
        row = (
            result['team_name'],
            result['short_name'],
            result['score']
        )
        rows.append(row)

    return rows


@register_sheet_handler('darts_playoff')
def handle_darts_playoff(data):
    headers = ('Круг', 'Игрок 1', 'Очки 1', 'Очки 2', 'Игрок 2')
    rows = [headers]

    for result in data:
        row = (
            result['playoff_type'],
            result['player1_name'],
            result['player1_wins'],
            result['player2_wins'],
            result['player2_name'],
        )
        rows.append(row)

    return rows


def process_sheet(sheet_name: str, raw_data):
    try:
        handler = sheet_handlers.get(sheet_name)
        if not handler:
            logger.info(f"[SKIP] No handler for sheet '{sheet_name}'")
            return
        values = handler(raw_data)

        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)

        sheet.clear()
        sheet.update(values, "A1")
        logger.info(f"[OK] Updated sheet: {sheet_name}")
    except Exception as e:
        logger.exception(f"[ERROR] Failed to update '{sheet_name}': {e}")


# === Основная функция ===
def update_multiple_sheets(sheet_data_map: Dict[str, Any], use_threads: bool = True):
    """
    Обновляет несколько листов в Google таблице, каждый по своей логике обработки.

    :param sheet_data_map: Словарь {название_листа: данные}
    :param use_threads: Использовать многопоточность для ускорения
    """

    if use_threads:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [executor.submit(process_sheet, sheet_name, data) for sheet_name, data in sheet_data_map.items()]
            for future in as_completed(futures):
                pass  # все логи уже выведены внутри process_sheet
    else:
        for sheet_name, data in sheet_data_map.items():
            process_sheet(sheet_name, data)


# update_multiple_sheets(test_data, True)
