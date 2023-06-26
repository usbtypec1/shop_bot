import structlog
from aiogram import Dispatcher

from . import users, admin, errors

logger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    errors.register_handlers(dispatcher)
    admin.register_handlers(dispatcher)
    users.register_handlers(dispatcher)
    logger.debug('Registered users handlers')
