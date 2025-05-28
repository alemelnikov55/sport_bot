from aiogram.types import Message
from aiogram_dialog import StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from database.football_requests import change_match_status
from database.models import MatchStatus
from handlers.judge.state import FootballStates


async def update(message: Message, session: AsyncSession, dialog_manager):
    # print(await change_match_status(2, MatchStatus.FINISHED, session))
    await dialog_manager.start(FootballStates.sport, mode=StartMode.RESET_STACK)
