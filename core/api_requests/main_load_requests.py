import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint

# Общие настройки
BASE_URL = "https://spartakiada.techincity.ru/referee-bot-integration/api/v1"
AUTH = HTTPBasicAuth("test", "123")  # Логин и пароль
SSL_VERIFY = False  # Отключаем проверку SSL для тестов

def make_api_request(endpoint):
    """Общая функция для выполнения GET-запросов к API"""
    url = f"{BASE_URL}/{endpoint}"
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
