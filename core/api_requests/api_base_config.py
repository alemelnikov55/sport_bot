import requests
from typing import Any, Dict, List
import urllib3

from loader import ApiSettings

API_URL = "https://spartakiada.techincity.ru/referee-bot-integration/api/v1/tournaments"
AUTH = ("test", "123")  # Basic Auth

# def send_tournament_stages(data: List[dict]) -> None:
#     try:
#         response = requests.post(
#             url=API_URL,
#             auth=AUTH,
#             json=data,
#             # verify=False,  # отключаем проверку SSL-сертификата (dev mode)
#             timeout=10
#         )
#         if response.status_code == 204:
#             print("✅ Турнирная сетка успешно отправлена.")
#         else:
#             print(f"❌ Ошибка {response.status_code}: {response.text}")
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Сетевая ошибка при отправке турнирной сетки: {e}")


class ExternalAPIClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
        timeout: int = 10
    ):
        self.base_url = base_url.rstrip("/")
        self.auth = (username, password)
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _post(self, endpoint: str, data: Any) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.post(
                url=url,
                json=data,
                auth=self.auth,
                verify=self.verify_ssl,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Ошибка при POST {url}: {e}")

    def send_tournament_stages(self, tournament_data: List[Dict]) -> None:
        response = self._post("/tournaments", tournament_data)
        print(f"✅ Турнирная сетка отправлена ({response.status_code})")

    def send_results(self, results_data: List[Dict]) -> None:
        response = self._post("/results", results_data)
        print(f"✅ Результаты отправлены ({response.status_code})")


api = ExternalAPIClient(
    base_url=ApiSettings.API_URL,
    username=ApiSettings.API_USER,
    password=ApiSettings.API_PASSWORD,
)
