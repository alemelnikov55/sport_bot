"""
Модуль для передачи scheduler в обработчики
"""
import dataclasses
from typing import Any, Callable, Dict, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from sqlalchemy import Update
from sqlalchemy.ext.asyncio import async_sessionmaker
from apscheduler_di import ContextSchedulerDecorator


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware для работы с БД
    """

    def __init__(self, session_pool: async_sessionmaker) -> None:
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            result = await handler(event, data)
            return result


@dataclasses.dataclass
class ApschedulerMiddleware(BaseMiddleware):
    """
    middelware для Добавления в сообщение scheduler
    """

    def __init__(self, scheduler: ContextSchedulerDecorator):
        self.scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        data['scheduler'] = self.scheduler
        result = await handler(event, data)
        return result
