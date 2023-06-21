import asyncio
import logging

import structlog
import tzlocal
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode, BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import backup.handlers
import cart.handlers
import categories.handlers
import common.handlers
import config
import mailing.handlers
import payments.handlers
import products.handlers
import shop_info.handlers
import support_tickets.handlers
import users.handlers
from cart.repositories import CartRepository
from categories.repositories import CategoryRepository
from common.middlewares import DependencyInjectMiddleware
from database import session_factory
from database.setup import init_tables
from products.repositories import ProductRepository
from services import notifications
from users.middlewares import BannedUserMiddleware, AdminIdentifierMiddleware
from users.repositories import UserRepository

logger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    backup.handlers.register_handlers(dispatcher)
    cart.handlers.register_handlers(dispatcher)
    categories.handlers.register_handlers(dispatcher)
    common.handlers.register_handlers(dispatcher)
    mailing.handlers.register_handlers(dispatcher)
    payments.handlers.register_handlers(dispatcher)
    products.handlers.register_handlers(dispatcher)
    shop_info.handlers.register_handlers(dispatcher)
    support_tickets.handlers.register_handlers(dispatcher)
    users.handlers.register_handlers(dispatcher)


async def set_default_commands(dispatcher: Dispatcher):
    await dispatcher.bot.set_my_commands(
        [
            BotCommand("start", "Start bot"),
            BotCommand('cancel', 'Cancel Command'),
        ]
    )


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)


def setup_logging():
    loglevel = logging.DEBUG if config.AppSettings().debug else logging.INFO
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(loglevel),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )


def main():
    bot = Bot(config.AppSettings().bot_token, parse_mode=ParseMode.HTML)
    dispatcher = Dispatcher(bot, storage=MemoryStorage())

    config.PRODUCT_UNITS_PATH.mkdir(parents=True, exist_ok=True)
    config.PRODUCT_PICTURE_PATH.mkdir(parents=True, exist_ok=True)

    scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    app_settings = config.AppSettings()
    admin_telegram_ids = app_settings.admins_id

    setup_logging()
    # tasks.setup_tasks(scheduler)

    init_tables()

    user_repository = UserRepository(session_factory)
    dispatcher.setup_middleware(BannedUserMiddleware(user_repository))
    dispatcher.setup_middleware(AdminIdentifierMiddleware(admin_telegram_ids))
    dispatcher.setup_middleware(
        DependencyInjectMiddleware(
            bot=bot,
            dispatcher=dispatcher,
            user_repository=user_repository,
            product_repository=ProductRepository(session_factory),
            category_repository=CategoryRepository(session_factory),
            cart_repository=CartRepository(session_factory),
        ),
    )

    register_handlers(dispatcher)

    setup_logging()

    try:
        executor.start_polling(
            dispatcher=dispatcher,
            on_startup=on_startup,
            skip_updates=True,
        )
    except RuntimeError as e:
        logger.critical("Error during bot starting!")
        asyncio.run(
            asyncio.run(notifications.ErrorNotification(e).send())
        )


if __name__ == "__main__":
    main()
