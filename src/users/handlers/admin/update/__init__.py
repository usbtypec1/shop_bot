from aiogram import Dispatcher

from . import is_banned, top_up

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    is_banned.register_handlers(dispatcher)
    top_up.register_handlers(dispatcher)
