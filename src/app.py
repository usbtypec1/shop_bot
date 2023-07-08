import asyncio
import logging

import structlog
import tzlocal
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode, BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import backup.handlers
import cart.handlers
import categories.handlers
import common.handlers
import config
import mailing.handlers
import payments.handlers
import products.handlers
import sales.handlers
import shop_info.handlers
import support.handlers
import time_sensitive_discounts.handlers
import top_up_bonuses.handlers
import users.handlers
from cart.repositories import CartRepository
from categories.repositories import CategoryRepository
from common.middlewares import DependencyInjectMiddleware
from common.services import AdminsNotificator
from common.views import ErrorView
from database.setup import init_tables
from payments.services.payments_apis import CoinbaseAPI
from products.repositories import ProductRepository
from sales.repositories import SaleRepository
from shop_info.repositories import ShopInfoRepository
from support.repositories import (
    SupportTicketRepository,
    SupportTicketReplyRepository,
)
from time_sensitive_discounts.repositories import (
    TimeSensitiveDiscountRepository,
)
from top_up_bonuses.repositories import TopUpBonusRepository
from users.middlewares import BannedUserMiddleware, AdminIdentifierMiddleware
from users.repositories import UserRepository

logger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    common.handlers.register_handlers(dispatcher)
    backup.handlers.register_handlers(dispatcher)
    cart.handlers.register_handlers(dispatcher)
    categories.handlers.register_handlers(dispatcher)
    mailing.handlers.register_handlers(dispatcher)
    payments.handlers.register_handlers(dispatcher)
    products.handlers.register_handlers(dispatcher)
    sales.handlers.register_handlers(dispatcher)
    shop_info.handlers.register_handlers(dispatcher)
    support.handlers.register_handlers(dispatcher)
    time_sensitive_discounts.handlers.register_handlers(dispatcher)
    top_up_bonuses.handlers.register_handlers(dispatcher)
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
    app_settings = config.AppSettings()

    bot = Bot(app_settings.bot_token, parse_mode=ParseMode.HTML)
    dispatcher = Dispatcher(bot, storage=MemoryStorage())

    config.PRODUCT_UNITS_PATH.mkdir(parents=True, exist_ok=True)
    config.MEDIA_FILES_PATH.mkdir(parents=True, exist_ok=True)

    scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    admin_telegram_ids = app_settings.admins_id

    engine = create_engine('sqlite:///../data/database.db')
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    setup_logging()
    # tasks.setup_tasks(scheduler)

    init_tables(engine)

    coinbase_settings = config.CoinbaseSettings()

    admins_notificator = AdminsNotificator(
        bot=bot,
        admin_ids=app_settings.admins_id,
    )

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
            sale_repository=SaleRepository(session_factory),
            time_sensitive_discount_repository=(
                TimeSensitiveDiscountRepository(session_factory)
            ),
            top_up_bonus_repository=TopUpBonusRepository(session_factory),
            coinbase_api=CoinbaseAPI(coinbase_settings.api_key),
            admins_notificator=admins_notificator,
            support_ticket_repository=SupportTicketRepository(session_factory),
            support_ticket_reply_repository=(
                SupportTicketReplyRepository(session_factory)
            ),
            shop_info_repository=ShopInfoRepository(session_factory),
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
    except RuntimeError as error:
        logger.critical("Error during bot starting!")
        view = ErrorView(error)
        asyncio.run(
            admins_notificator.notify(
                text=view.get_text(),
                reply_markup=view.get_reply_markup(),
            ),
        )


if __name__ == "__main__":
    main()
