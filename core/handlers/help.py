from aiogram.types import Message, BotCommandScopeChat
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession


async def help_handler(message: Message, bot: Bot, session: AsyncSession) -> None:
    """
    Обработчик команды /help.
    """
    help_text = ('Доступные команды:\n'
                 '/help - показать это сообщение\n'
                 '/start - начать взаимодействие с ботом\n'
                 '/cancel - сбросить память диалога\n'
                 '/panel - показать панель администратора\n'
                 '/choose_sport - выбрать вид спорта для судейства\n'
                 '/start_game - начать обновление турнирных таблиц\n')
    await message.answer(help_text)