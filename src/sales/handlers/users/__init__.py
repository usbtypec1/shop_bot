from aiogram import Dispatcher

from . import buy

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    buy.register_handlers(dispatcher)
