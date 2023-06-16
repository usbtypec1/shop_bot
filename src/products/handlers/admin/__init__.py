from aiogram import Dispatcher

from . import categories

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    categories.register_handlers(dispatcher)
