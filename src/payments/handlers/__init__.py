import structlog
from aiogram import Dispatcher
from structlog.stdlib import BoundLogger

from . import admin, users

__all__ = ('register_handlers',)

logger: BoundLogger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    admin.register_handlers(dispatcher)
    users.register_handlers(dispatcher)
    logger.debug('Registered payments handlers')
