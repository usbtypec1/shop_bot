from aiogram import Dispatcher

from . import status, answer

__all__ = (
    'status',
    'answer',
)


def register_handlers(dispatcher: Dispatcher) -> None:
    status.register_handlers(dispatcher)
    answer.register_handlers(dispatcher)
