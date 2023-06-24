from aiogram import Dispatcher

from . import is_banned

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    is_banned.register_handlers(dispatcher)
