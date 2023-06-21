from aiogram import Dispatcher

from . import users

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    users.register_handlers(dispatcher)
