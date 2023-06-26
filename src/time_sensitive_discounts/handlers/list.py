from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType

from common.filters import AdminFilter

__all__ = ('register_handlers',)


async def on_show_active_time_sensitive_discounts(
        message: Message,
        state: FSMContext,
) -> None:
    pass


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_active_time_sensitive_discounts,
        AdminFilter(),
        Text('% View Active Discounts'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
