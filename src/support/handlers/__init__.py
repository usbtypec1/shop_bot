import structlog
from aiogram import Dispatcher
from structlog.stdlib import BoundLogger

from . import users, admin, replies

__all__ = ('register_handlers',)

logger: BoundLogger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    admin.register_handlers(dispatcher)
    users.register_handlers(dispatcher)
    replies.register_handlers(dispatcher)
    logger.debug('Registered support tickets handlers')
