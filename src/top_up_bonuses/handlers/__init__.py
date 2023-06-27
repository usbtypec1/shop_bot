from aiogram import Dispatcher

from . import list, menu, create

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    list.register_handlers(dispatcher)
    menu.register_handlers(dispatcher)
    create.register_handlers(dispatcher)
