from aiogram import Dispatcher

from . import delete

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    delete.register_handlers(dispatcher)
