from aiogram import Dispatcher

from . import menu, update

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    menu.register_handlers(dispatcher)
    update.register_handlers(dispatcher)
