from aiogram import Dispatcher

from . import detail

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    detail.register_handlers(dispatcher)
