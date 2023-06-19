import structlog
from aiogram import Dispatcher

from . import admin, users

__all__ = ('register_handlers',)

logger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    # users.register_handlers(dispatcher)
    admin.register_handlers(dispatcher)
    logger.debug('Registered products handlers')
