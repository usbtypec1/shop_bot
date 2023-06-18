from aiogram import Dispatcher

from . import list, detail, create, update

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    list.register_handlers(dispatcher)
    detail.register_handlers(dispatcher)
    create.register_handlers(dispatcher)
    update.register_handlers(dispatcher)
