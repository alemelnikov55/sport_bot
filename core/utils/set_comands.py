from aiogram.types import BotCommand, BotCommandScopeChat

SUPERUSER_COMMANDS = [
    BotCommand(command='panel', description='Панель администратора'),
    BotCommand(command='start_game', description='Начать игру'),
    BotCommand(command='choose_sport', description='Выбрать вид спорта'),
    BotCommand(command='cancel', description='Отменить действие'),
    BotCommand(command='help', description='Небольшая подсказка'),
    BotCommand(command='start', description='Обновить статусы'),
]

ADMIN_COMMANDS = [
    BotCommand(command='panel', description='Панель администратора'),
    BotCommand(command='start_game', description='Начать игру'),
    BotCommand(command='choose_sport', description='Выбрать вид спорта'),
    BotCommand(command='cancel', description='Отменить действие'),
    BotCommand(command='help', description='Небольшая подсказка'),
    BotCommand(command='start', description='Обновить статусы'),
]

JUDGE_COMMANDS = [
    BotCommand(command='choose_sport', description='Выбрать вид спорта'),
    BotCommand(command='cancel', description='Отменить действие'),
    BotCommand(command='help', description='Небольшая подсказка'),
    BotCommand(command='start', description='Обновить статусы'),
]

