import requests
from typing import List

API_URL = "https://spartakiada.techincity.ru/referee-bot-integration/api/v1/tournament-stages"
AUTH = ("test", "123")  # Basic Auth

def send_tournament_stages(data: List[dict]) -> None:
    try:
        response = requests.post(
            url=API_URL,
            auth=AUTH,
            json=data,
            # verify=False,  # отключаем проверку SSL-сертификата (dev mode)
            timeout=10
        )
        if response.status_code == 200:
            print("✅ Турнирная сетка успешно отправлена.")
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Сетевая ошибка при отправке турнирной сетки: {e}")
