from aiogram import Dispatcher

from . import (
    profile,
    statistics,
)

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    profile.register_handlers(dispatcher)
    statistics.register_handlers(dispatcher)
