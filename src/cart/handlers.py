from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType

from cart.views import UserShoppingCartView
from common.views import answer_view

__all__ = ('register_handlers',)


async def on_show_shopping_cart(
        message: Message,
        state: FSMContext,
) -> None:
    view = UserShoppingCartView([])
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_shopping_cart,
        Text('🛒 Cart'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
