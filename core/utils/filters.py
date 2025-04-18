"""
Фильтры для определения ролей
"""
from typing import List
import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.service_requests import get_all_judges, get_all_admins
from loader import MainSettings

logger = logging.getLogger(__name__)


class IsAdmin(BaseFilter):
    """Проверка, является ли пользователь администратором."""

    async def __call__(self, message: Message, **data):
        session = data.get('session')
        admins = await get_all_admins(session)
        if message.from_user.id in admins or message.from_user.id == MainSettings.SUPERUSER:
            return True
        await message.answer('Вы не являетесь администратором соревнования.')
        logger.info('False')
        return False


class IsJudge(BaseFilter):
    """Проверка, является ли пользователь администратором."""

    async def __call__(self, message: Message, **data):
        session = data.get('session')
        judges = await get_all_judges(session)
        if message.from_user.id in judges or message.from_user.id == MainSettings.SUPERUSER:
            return True
        await message.answer('Вы не являетесь судьей соревнования.')
        logger.info('False')
        return False
