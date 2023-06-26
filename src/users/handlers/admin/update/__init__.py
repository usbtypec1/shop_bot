from aiogram import Dispatcher

from . import is_banned, balance, max_cart_cost, permanent_discount

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    is_banned.register_handlers(dispatcher)
    max_cart_cost.register_handlers(dispatcher)
    balance.register_handlers(dispatcher)
    permanent_discount.register_handlers(dispatcher)
