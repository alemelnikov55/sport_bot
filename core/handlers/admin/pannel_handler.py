from aiogram.types import Message
from aiogram_dialog import DialogManager
import logging

from handlers.judge.state import AdminStates


async def start_admin_panel(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminStates.start_menu)
