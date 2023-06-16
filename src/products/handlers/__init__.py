import structlog
from aiogram import Dispatcher

from . import admin

__all__ = ('register_handlers',)

logger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    admin.register_handlers(dispatcher)
    logger.debug('Registered products handlers')
