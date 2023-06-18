from aiogram import Dispatcher

from . import categories, products

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    categories.register_handlers(dispatcher)
    products.register_handlers(dispatcher)
