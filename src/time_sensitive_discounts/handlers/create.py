from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType

from common.filters import AdminFilter

__all__ = ('register_handlers',)


async def on_start_time_sensitive_discount_creation_flow(
        message: Message,
        state: FSMContext,
) -> None:
    pass


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_start_time_sensitive_discount_creation_flow,
        AdminFilter(),
        Text('Create New Discount'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
