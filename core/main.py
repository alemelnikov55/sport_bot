import asyncio
import logging

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

from aiohttp import web

# from handlers.admin.admin_callback_handler import admin_callback_handler
from handlers.admin.pannel_handler import start_admin_panel
from handlers.admin.start_game import start_game
# from handlers.judge.dialog import football_dialog
from loader import RedisSettings, MainSettings, WebhookSettings

from handlers.support_handlers import start_bot_sup_handler, stop_bot_sup_handler
from handlers.update import update

# from handlers.admin.create_football_group import get_teams_amount

from handlers.judge.choose_sport import choose_sport
from handlers.judge.dialog import dialog_router
from utils.filters import IsAdmin
# from handlers.judge.callback_handlers import judge_callback_handler
from utils.middleware import DatabaseMiddleware, ApschedulerMiddleware

from database.models import async_session

from aiogram_dialog import setup_dialogs

from utils.states import GroupCreationStates

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


async def start_bot():
    """Запуск бота и его обработчиков"""

    # Создаем хранилище состояний
    storage = RedisStorage(r, key_builder=DefaultKeyBuilder(with_destiny=True))
    bot = Bot(token=MainSettings.TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher(storage=storage)

    # Создаем планировщик задач
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Europe/Moscow', jobjobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.start()

    dp.include_router(dialog_router)

    dp.update.middleware(DatabaseMiddleware(session_pool=async_session))
    dp.update.middleware.register(ApschedulerMiddleware(scheduler))

    dp.startup.register(start_bot_sup_handler)
    dp.shutdown.register(stop_bot_sup_handler)

    dp.message.register(update, Command('update'))

    # Регистрируем хэндлеры судей
    dp.message.register(choose_sport, Command('choose_sport'))

    # Регистрируем хэндлеры админов
    # dp.message.register(create_football_group, Command('create_football_group'), IsAdmin())
    dp.message.register(start_game, Command('start_game'), IsAdmin())
    # dp.message.register(get_teams_amount, GroupCreationStates.get_teams_amount)
    dp.message.register(start_admin_panel, Command('panel'), IsAdmin())

    # dp.callback_query.register(admin_callback_handler, F.data.startswith('adm'), IsAdmin())

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
