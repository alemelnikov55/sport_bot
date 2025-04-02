from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.service_requests import get_all_sports


async def choose_sport_handler(message: Message, state: FSMContext):
    """
    Стартовый хэндлер для выбора спорта. /choose_sport

    предоставляет клавиатуру с кнопками для выбора спорта
    :param message:
    :param state:
    :return:
    """
    await message.answer("выбери вид спорта:", reply_markup=await choose_sport_kb())


async def choose_sport_kb() -> InlineKeyboardMarkup:
    rb_builder = InlineKeyboardBuilder()

    sports = await get_all_sports()

    for sport_name, sport_id in sports.items():
        rb_builder.button(text=sport_name, callback_data=f'j_{sport_id}_s_c_-')

    rb_builder.adjust(2)

    return rb_builder.as_markup()
