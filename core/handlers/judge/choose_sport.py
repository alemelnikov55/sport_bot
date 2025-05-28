from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from aiogram_dialog import StartMode, DialogManager

from handlers.judge.state import MainJudgeStates


async def choose_sport(message: Message, dialog_manager: DialogManager, state: FSMContext):
    """
    Стартовый хэндлер для выбора спорта. /choose_sport

    предоставляет клавиатуру с кнопками для выбора спорта
    :param message:
    :param state:
    :param dialog_manager
    :return:
    """
    await state.clear()
    await dialog_manager.start(MainJudgeStates.sport, mode=StartMode.RESET_STACK)
