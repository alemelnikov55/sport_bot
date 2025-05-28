from aiogram.types import Message, BotCommandScopeChat
from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from database.service_requests import get_all_judges
from utils.set_comands import ADMIN_COMMANDS, JUDGE_COMMANDS, SUPERUSER_COMMANDS
from loader import MainSettings

command_mapping = {
    'admin': ADMIN_COMMANDS,
    'judge': JUDGE_COMMANDS,
    'superuser': SUPERUSER_COMMANDS
}


async def start_handler(message: Message, bot: Bot, session: AsyncSession):
    """
    Handler for the /start command.
    Sends a welcome message to the user.
    """
    user_id = message.from_user.id

    judges = await get_all_judges(session)
    superuser_id = MainSettings.SUPERUSER
    admin_ids = MainSettings.ADMIN_LIST

    if user_id == superuser_id:
        role = 'superuser'
    elif user_id in admin_ids:
        role = 'admin'
    elif user_id in judges:
        role = 'judge'
    else:
        await message.answer('У вас нет прав для использования команд бота. Обратитесь к администратору для получения доступа.')
        return

    await bot.set_my_commands(command_mapping[role], scope=BotCommandScopeChat(chat_id=user_id))
    await message.answer(
        "Добро пожаловать! Я бот для управления спортивными мероприятиями. "
        "Используйте команды для взаимодействия со мной."
    )
