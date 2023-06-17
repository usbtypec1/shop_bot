from aiogram import Dispatcher

from . import (
    balance,
    buy_product,
    profile,
    statistics,
    support,
)

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    balance.register_handlers(dispatcher)
    buy_product.register_handlers(dispatcher)
    profile.register_handlers(dispatcher)
    statistics.register_handlers(dispatcher)
    support.register_handlers(dispatcher)
