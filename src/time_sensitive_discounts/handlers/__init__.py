import structlog
from aiogram import Dispatcher
from structlog.stdlib import BoundLogger

from . import menu, create, list, detail, delete, update

__all__ = ('register_handlers',)

logger: BoundLogger = structlog.get_logger('app')


def register_handlers(dispatcher: Dispatcher) -> None:
    menu.register_handlers(dispatcher)
    create.register_handlers(dispatcher)
    list.register_handlers(dispatcher)
    detail.register_handlers(dispatcher)
    delete.register_handlers(dispatcher)
    update.register_handlers(dispatcher)
    logger.debug('Registered time sensitive discounts handlers')
