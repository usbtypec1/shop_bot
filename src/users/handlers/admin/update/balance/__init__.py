from aiogram import Dispatcher

from . import top_up

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    top_up.register_handlers(dispatcher)
