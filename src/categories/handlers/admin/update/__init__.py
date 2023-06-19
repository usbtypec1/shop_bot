from aiogram import Dispatcher

from . import (
    name,
    icon,
    max_displayed_stock_count,
    priority,
    hidden_status,
    can_be_seen_status,
)

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    for module in (
            name,
            icon,
            max_displayed_stock_count,
            priority,
            hidden_status,
            can_be_seen_status,
    ):
        module.register_handlers(dispatcher)
