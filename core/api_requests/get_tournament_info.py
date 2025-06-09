"""
Модуль для зашруки информации из внешней системы
"""
import asyncio
from pprint import pprint

from api_requests.inpout_requests import import_external_athletes, import_external_teams, import_external_sports

from database.models.engine import async_session


import requests
from requests.auth import HTTPBasicAuth
from loader import ApiSettings

# Общие настройки
AUTH = HTTPBasicAuth(ApiSettings.API_USER, ApiSettings.API_PASSWORD)  # Логин и пароль

def make_api_request(endpoint):
    """Общая функция для выполнения GET-запросов к API"""
    url = f"{ApiSettings.API_URL}/{endpoint}"
    try:
        response = requests.get(url, auth=AUTH)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка {response.status_code} для {endpoint}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка при запросе к {endpoint}: {e}")
        return None

def get_athletes():
    """Получение списка атлетов"""
    print("🔄 Запрос списка атлетов...")
    athletes = make_api_request("athletes")['items']
    if athletes:
        print(f"✅ Получено атлетов: {len(athletes)}")
    return athletes

def get_divisions():
    """Получение списка дивизионов"""
    print("🔄 Запрос списка дивизионов...")
    divisions = make_api_request("divisions")['items']
    if divisions:
        print(f"✅ Получено дивизионов: {len(divisions)}")
    return divisions

def get_disciplines():
    """Получение списка дисциплин (для полноты)"""
    print("🔄 Запрос списка дисциплин...")
    disciplines = make_api_request("disciplines")['items']
    if disciplines:
        print(f"✅ Получено дисциплин: {len(disciplines)}")
    return disciplines



async def get_tournament_full_info():
    athletes = get_athletes()
    # teams = get_divisions()
    # sports = get_disciplines()
    #
    # pprint(teams)
    # pprint(sports)

    async with async_session() as session:
    #     # 2. Импортируем команды
    #     print("🔄 Импортируем команды...")
    #     await import_external_teams(session, teams)
    #
    #     # 3. Импортируем виды спорта
    #     print("🔄 Импортируем виды спорта...")
    #     await import_external_sports(session, sports)
    #
        # 1. Импортируем атлетов
        print("🔄 Импортируем атлетов...")
        await import_external_athletes(session, athletes)


if __name__ == "__main__":
    asyncio.run(get_tournament_full_info())


