from aiogram import Dispatcher

from . import create, list

__all__ = (
    'create',
    'list',
)


def register_handlers(dispatcher: Dispatcher) -> None:
    create.register_handlers(dispatcher)
    list.register_handlers(dispatcher)
