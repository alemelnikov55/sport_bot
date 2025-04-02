from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import change_match_status
from database.models import MatchStatus


async def update(message: Message, session: AsyncSession):
    print(await change_match_status(2, MatchStatus.FINISHED, session))
    await message.reply("Обновление успешно")
