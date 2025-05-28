import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.fsm.storage import redis
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from aiogram_dialog import setup_dialogs

from aiohttp import web

from handlers.text_handler import text_handler
from loader import RedisSettings, MainSettings, WebhookSettings
from logger_config import LOGGING_CONFIG

from handlers.support_handlers import start_bot_sup_handler, stop_bot_sup_handler
from handlers.cancel_handler import cancel_handler
from handlers.start import start_handler

from handlers.admin.pannel_handler import start_admin_panel
from handlers.admin.start_game import start_game

from handlers.update import update

from handlers.judge.choose_sport import choose_sport
from handlers.judge.dialog import dialog_router

from utils.filters import IsAdmin, IsJudge
from utils.middleware import DatabaseMiddleware, ApschedulerMiddleware

from database.models import async_session

"""add smth"""
r = redis.Redis(host=RedisSettings.REDIS_HOST, port=RedisSettings.REDIS_PORT, db=0, decode_responses=True)

jobstores = {
    'default': RedisJobStore(
        jobs_key='dispatcher_trips_jobs',
        run_times_key='dispatcher_trips_running',
        host='localhost',
        db=2,
        port=6379,
    )
}
"""init commit"""
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

logging.getLogger("apscheduler").setLevel(logging.WARNING)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiogram.dispatcher").setLevel(logging.WARNING)


async def start_bot():
    """Запуск бота и его обработчиков"""

    # Создаем хранилище состояний
    storage = RedisStorage(r, key_builder=DefaultKeyBuilder(with_destiny=True))
    bot = Bot(token=MainSettings.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)
    dp.include_router(dialog_router)
    # Создаем планировщик задач
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Europe/Moscow', jobjobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.start()

    dp.update.middleware(DatabaseMiddleware(session_pool=async_session))
    dp.update.middleware.register(ApschedulerMiddleware(scheduler))

    dp.startup.register(start_bot_sup_handler)
    dp.shutdown.register(stop_bot_sup_handler)

    # dp.message.register(update, Command('update'))
    dp.message.register(cancel_handler, Command('cancel'))
    dp.message.register(start_handler, Command('start'))

    # Регистрируем хэндлеры судей
    dp.message.register(choose_sport, Command(commands='choose_sport'), IsJudge())

    # Регистрируем хэндлеры админов
    dp.message.register(start_game, Command('start_game'), IsAdmin())
    dp.message.register(start_admin_panel, Command('panel'), IsAdmin())
    # dp.message.register(text_handler, F.text)

    setup_dialogs(dp)

    try:
        if not WebhookSettings.WEBHOOK_DOMAIN:
            await bot.delete_webhook()
            logger.info('Бот запущен в режиме поллинга')
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
