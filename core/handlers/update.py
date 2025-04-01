from aiogram.types import Message


async def update(message: Message):
    await message.reply("Обновление успешно")