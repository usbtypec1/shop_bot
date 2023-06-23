from aiogram import Dispatcher

from . import menu, products

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    menu.register_handlers(dispatcher)
    products.register_handlers(dispatcher)
