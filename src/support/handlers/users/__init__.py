from aiogram import Dispatcher

from . import menu, create, list, detail

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    menu.register_handlers(dispatcher)
    create.register_handlers(dispatcher)
    list.register_handlers(dispatcher)
    detail.register_handlers(dispatcher)
