from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.filters import AdminFilter


async def on_show_products_list(
        message: Message,
) -> None:
    pass


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_products_list,
        Text('📝 Products Management'),
        AdminFilter(),
        state='*',
    )
