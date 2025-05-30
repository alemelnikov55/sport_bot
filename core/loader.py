"""
Модуль констант для работы бота
"""
import dataclasses
import os

from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Файл .env не найден. Переменные не загружены')
else:
    load_dotenv()


@dataclasses.dataclass
class MainSettings:
    TOKEN = os.getenv('TOKEN')
    SUPERUSER = int(os.getenv('SUPERUSER'))
    ADMIN_GROUP = int(os.getenv('ADMIN_GROUP'))


class DBSettings:
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_PORT = os.getenv('DB_PORT')


class RedisSettings:
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')


class WebhookSettings:
    WEBHOOK_DOMAIN = os.getenv('WEBHOOK_DOMAIN')
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
    APP_HOST = os.getenv('APP_HOST')
    APP_PORT = os.getenv('APP_PORT')


class ApiSettings:
    API_URL = os.getenv('API_URL')
    API_USER = os.getenv('API_USER')
    API_PASSWORD = os.getenv('API_PASSWORD')

groups_type = [{'name': '1/8', 'id': '1/8'},
               {'name': '1/4', 'id': '1/4'},
               {'name': '1/2', 'id': '1/2'},
               {'name': 'Фин', 'id': 'Фин'},
               {'name': 'За 3', 'id': 'За 3'}]
