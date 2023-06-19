from aiogram import Dispatcher

from . import (
    name,
    description,
    price,
    min_order_quantity,
    max_order_quantity,
    max_replacement_time,
    max_displayed_stock,
    is_duplicated_stock_entries_allowed,
    is_hidden,
    can_be_purchased,
    permitted_gateways,
    media,
)

__all__ = ('register_handlers',)


def register_handlers(dispatcher: Dispatcher) -> None:
    name.register_handlers(dispatcher)
    description.register_handlers(dispatcher)
    price.register_handlers(dispatcher)
    min_order_quantity.register_handlers(dispatcher)
    max_order_quantity.register_handlers(dispatcher)
    max_replacement_time.register_handlers(dispatcher)
    max_displayed_stock.register_handlers(dispatcher)
    is_duplicated_stock_entries_allowed.register_handlers(dispatcher)
    is_hidden.register_handlers(dispatcher)
    can_be_purchased.register_handlers(dispatcher)
    permitted_gateways.register_handlers(dispatcher)
    media.register_handlers(dispatcher)
