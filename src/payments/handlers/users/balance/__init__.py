from aiogram import Dispatcher

from . import menu, top_up

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    menu.register_handlers(dispatcher)
    top_up.register_handlers(dispatcher)
