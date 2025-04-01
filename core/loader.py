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
    ADMIN_LIST = [int(x) for x in os.getenv('ADMIN_LIST').split(' ')]


class DBSettings:
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    DB_PORT = os.getenv('DB_PORT')


class RedisSettings:
    REDIS_HOST = os.getenv('REDIS_HOST')


class WebhookSettings:
    WEBHOOK_DOMAIN = os.getenv('WEBHOOK_DOMAIN')
    WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
    APP_HOST = os.getenv('APP_HOST')
    APP_PORT = os.getenv('APP_PORT')
