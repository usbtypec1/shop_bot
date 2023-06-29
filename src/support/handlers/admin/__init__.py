from aiogram import Dispatcher

from . import menu, list, detail, delete, update, search

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    list.register_handlers(dispatcher)
    detail.register_handlers(dispatcher)
    update.register_handlers(dispatcher)
    delete.register_handlers(dispatcher)
    menu.register_handlers(dispatcher)
    search.register_handlers(dispatcher)
