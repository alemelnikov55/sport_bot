from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_dialog import DialogManager


async def cancel_handler(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await state.clear()
    await dialog_manager.reset_stack()
