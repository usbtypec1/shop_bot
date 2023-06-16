from aiogram import Dispatcher

from . import admin

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    admin.register_handlers(dispatcher)
