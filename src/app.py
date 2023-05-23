import asyncio
import logging

import structlog
import aiogram
from aiogram import executor

import config
import handlers
import middlewares
import tasks
from services import db_api
from services import notifications
from services.db_api.setup import init_tables

logger = structlog.get_logger('app')


async def set_default_commands(dispatcher: aiogram.Dispatcher):
    await dispatcher.bot.set_my_commands(
        [
            aiogram.types.BotCommand("start", "Start bot"),
            aiogram.types.BotCommand('cancel', 'Cancel Command'),
        ]
    )


async def on_startup(dispatcher):
    config.PRODUCT_UNITS_PATH.mkdir(parents=True, exist_ok=True)
    config.PRODUCT_PICTURE_PATH.mkdir(parents=True, exist_ok=True)
    tasks.setup_tasks()
    init_tables()
    middlewares.setup_middlewares(dispatcher)
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


if __name__ == "__main__":
    setup_logging()
    try:
        executor.start_polling(handlers.dp, on_startup=on_startup, skip_updates=True)
    except RuntimeError as e:
        logger.critical("Error during bot starting!")
        asyncio.run(
            asyncio.run(notifications.ErrorNotification(e).send())
        )

