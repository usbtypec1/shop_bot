from aiogram import Dispatcher

from . import menu, create, list, detail, replies

__all__ = (
    'menu',
    'create',
    'list',
    'detail',
    'replies',
)


def register_handlers(dispatcher: Dispatcher) -> None:
    menu.register_handlers(dispatcher)
    create.register_handlers(dispatcher)
    list.register_handlers(dispatcher)
    detail.register_handlers(dispatcher)
    replies.register_handlers(dispatcher)
