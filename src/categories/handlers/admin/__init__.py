from aiogram import Dispatcher

from . import create, delete, list, detail, update

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    for module in (
            create,
            delete,
            list,
            detail,
            update,
    ):
        module.register_handlers(dispatcher)
