from aiogram import Dispatcher

from . import users, admin


def register_handlers(dispatcher: Dispatcher) -> None:
    admin.register_handlers(dispatcher)
    users.register_handlers(dispatcher)
