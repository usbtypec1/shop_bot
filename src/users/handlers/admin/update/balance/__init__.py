from aiogram import Dispatcher

from . import top_up, set_specific

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    top_up.register_handlers(dispatcher)
    set_specific.register_handlers(dispatcher)
