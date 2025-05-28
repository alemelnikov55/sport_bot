"""
Вспомогательные команды для оповещения администратора и страта бота
"""
from datetime import datetime

from aiogram import Bot
from aiogram.types import BotCommandScopeAllGroupChats, BotCommand, BotCommandScopeAllPrivateChats

from loader import MainSettings


async def set_commands(bot: Bot):
    """
    Дбавляет команды бота в меню
    """
    await bot.delete_my_commands()
    await bot.set_my_commands([
        BotCommand(command='play', description='Выводит список заданий'),
        BotCommand(command='register', description='Регистрация команды'),
        BotCommand(command='score', description='Таблица результатов'),
        BotCommand(command='help', description='Раздел с игровыми командами'),
    ])
    await bot.set_my_commands([
        BotCommand(command='update', description='Обновить список заданий'),
    ],
        BotCommandScopeAllGroupChats())
    await bot.set_my_commands([
        BotCommand(command='table', description='Таблица прогресса игры'),
    ],
        BotCommandScopeAllPrivateChats())


async def start_bot_sup_handler(bot: Bot) -> None:
    """Запуск бота

    Отправляет сообщение админимтратору и запускает процесс создания и проверки БД
    """
    await bot.send_message(MainSettings.SUPERUSER, 'Бот запущен')


async def stop_bot_sup_handler(bot: Bot) -> None:
    """Остановка бота"""
    await bot.send_message(MainSettings.SUPERUSER, 'Бот остановлен')
