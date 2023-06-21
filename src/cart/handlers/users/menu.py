from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType, CallbackQuery

from cart.callback_data import CartProductDeleteCallbackData
from cart.repositories import CartRepository
from cart.views import UserShoppingCartView
from common.views import answer_view, edit_message_by_view

__all__ = ('register_handlers',)


async def on_delete_cart_product_in_shopping_cart(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        cart_repository: CartRepository,
) -> None:
    await state.finish()
    cart_product_id: int = callback_data['cart_product_id']
    cart_repository.delete_by_id(cart_product_id)
    cart_products = cart_repository.get_cart_products(
        user_telegram_id=callback_query.from_user.id,
    )
    view = UserShoppingCartView(cart_products)
    await edit_message_by_view(message=callback_query.message, view=view)


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
    dispatcher.register_callback_query_handler(
        on_delete_cart_product_in_shopping_cart,
        CartProductDeleteCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_shopping_cart,
        Text('🛒 Cart'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
