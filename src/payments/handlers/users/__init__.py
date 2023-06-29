from aiogram import Dispatcher

from . import balance

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    balance.register_handlers(dispatcher)
