from aiogram.types import Message


async def text_handler(message: Message):
    await message.answer('Это сообщение не является командой.')
