from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def start(message: Message, state: FSMContext):
    await message.reply("выбери вид спорта", reply_markup=await choose_sport_kb())


async def choose_sport_kb() -> InlineKeyboardMarkup:
    rb_builder = InlineKeyboardBuilder()

    for sport in sports:
        rb_builder.button(text=sport.name, callback_data=sport.code)

    rb_builder.adjust(1)

    return rb_builder.as_markup()