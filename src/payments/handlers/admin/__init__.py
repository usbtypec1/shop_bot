from aiogram import Dispatcher

from . import manage

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    manage.register_handlers(dispatcher)
