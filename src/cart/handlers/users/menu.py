from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType

from cart.repositories import CartRepository
from cart.views import UserShoppingCartView
from common.views import answer_view

__all__ = ('register_handlers',)


async def on_show_shopping_cart(
        message: Message,
        state: FSMContext,
        cart_repository: CartRepository,
) -> None:
    await state.finish()
    cart_products = cart_repository.get_cart_products(
        user_telegram_id=message.from_user.id,
    )
    view = UserShoppingCartView(cart_products)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_shopping_cart,
        Text('🛒 Cart'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
