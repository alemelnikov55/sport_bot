import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage import redis
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from aiohttp import web

# from handlers.judge.dialog import football_dialog
from loader import RedisSettings, MainSettings, WebhookSettings

from handlers.support_handlers import start_bot_sup_handler, stop_bot_sup_handler
from handlers.update import update

from handlers.judge.choose_sport import choose_sport
from handlers.judge.dialog import dialog_router
from handlers.judge.callback_handlers import judge_callback_handler
from utils.middleware import DatabaseMiddleware

from database.models import async_session

from aiogram_dialog import setup_dialogs

r = redis.Redis(host='127.0.0.1', port=6379, db=0, decode_responses=True)


async def start_bot():
    """Запуск бота и его обработчиков"""

    # Создаем хранилище состояний
    storage = RedisStorage(r, key_builder=DefaultKeyBuilder(with_destiny=True))
    # storage.key_builder(DefaultKeyBuilder(with_destiny=True))
    # RedisStorage(key_builder=DefaultKeyBuilder(with_destiny=True))
    # DefaultKeyBuilder(with_destiny=True)
    bot = Bot(token=MainSettings.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)

    dp.include_router(dialog_router)

    dp.update.middleware(DatabaseMiddleware(session_pool=async_session))

    dp.startup.register(start_bot_sup_handler)
    dp.shutdown.register(stop_bot_sup_handler)

    dp.message.register(update, Command('update'))

    # dp.callback_query.register(judge_callback_handler, F.data.startswith('j'))
    dp.message.register(choose_sport, Command('choose_sport'))

    setup_dialogs(dp)

    try:
        if not WebhookSettings.WEBHOOK_DOMAIN:
            await bot.delete_webhook()
            await dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types()
            )
        else:
            aiohttp_logger = logging.getLogger('aiohttp.access')
            aiohttp_logger.setLevel(logging.DEBUG)

            await bot.set_webhook(
                url=WebhookSettings.WEBHOOK_DOMAIN + WebhookSettings.WEBHOOK_PATH,
                drop_pending_updates=True,
                allowed_updates=dp.resolve_used_update_types()
            )

            app = web.Application()
            SimpleRequestHandler(dispatcher=dp,
                                 bot=bot).register(app, path=WebhookSettings.WEBHOOK_PATH)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host=WebhookSettings.APP_HOST, port=WebhookSettings.APP_PORT)
            await site.start()

            await asyncio.Event().wait()
    except RuntimeError:
        pass
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_bot())
