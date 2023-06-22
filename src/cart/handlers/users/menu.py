from typing import Literal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType, CallbackQuery

from cart.callback_data import (
    CartProductDeleteCallbackData, CartProductQuantityUpdateCallbackData,
)
from cart.repositories import CartRepository
from cart.services import validate_product_quantity_change
from cart.states import UserShoppingCartDeleteAllStates
from cart.views import (
    UserShoppingCartView,
    UserShoppingCartDeleteAllAskForConfirmationView
)
from common.views import answer_view, edit_message_by_view

__all__ = ('register_handlers',)

from products.repositories import ProductRepository


async def on_product_quantity_update_in_shopping_cart(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        cart_repository: CartRepository,
        product_repository: ProductRepository,
) -> None:
    cart_product_id: int = callback_data['cart_product_id']
    action: Literal['increment', 'decrement'] = callback_data['action']
    cart_product = cart_repository.get_by_id(cart_product_id)
    product = product_repository.get_by_id(cart_product.product.id)

    will_be_changed_to = (
        cart_product.quantity + 1 if action == 'increment'
        else cart_product.quantity - 1
    )

    validate_product_quantity_change(
        product=product,
        cart_product_quantity=cart_product.quantity,
        will_be_changed_to=will_be_changed_to,
    )
    cart_repository.update_quantity(
        product_id=product.id,
        quantity=will_be_changed_to,
        cart_product_id=cart_product_id,
    )
    cart_products = cart_repository.get_cart_products(
        user_telegram_id=callback_query.from_user.id,
    )
    view = UserShoppingCartView(cart_products)
    await edit_message_by_view(message=callback_query.message, view=view)
    await state.finish()


async def on_delete_all_cart_products_in_shopping_cart(
        callback_query: CallbackQuery,
) -> None:
    await UserShoppingCartDeleteAllStates.confirm.set()
    await edit_message_by_view(
        message=callback_query.message,
        view=UserShoppingCartDeleteAllAskForConfirmationView(),
    )


async def on_delete_all_cart_products_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        cart_repository: CartRepository,
) -> None:
    cart_repository.delete_by_user_telegram_id(callback_query.from_user.id)
    cart_products = cart_repository.get_cart_products(
        user_telegram_id=callback_query.from_user.id,
    )
    view = UserShoppingCartView(cart_products)
    await edit_message_by_view(message=callback_query.message, view=view)
    await state.finish()


async def on_delete_cart_product_in_shopping_cart(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        cart_repository: CartRepository,
) -> None:
    cart_product_id: int = callback_data['cart_product_id']
    cart_repository.delete_by_id(cart_product_id)
    cart_products = cart_repository.get_cart_products(
        user_telegram_id=callback_query.from_user.id,
    )
    view = UserShoppingCartView(cart_products)
    await edit_message_by_view(message=callback_query.message, view=view)
    await state.finish()


async def on_show_shopping_cart(
        message_or_callback_query: Message | CallbackQuery,
        state: FSMContext,
        cart_repository: CartRepository,
) -> None:
    cart_products = cart_repository.get_cart_products(
        user_telegram_id=message_or_callback_query.from_user.id,
    )
    view = UserShoppingCartView(cart_products)
    if isinstance(message_or_callback_query, Message):
        await answer_view(message=message_or_callback_query, view=view)
    else:
        await edit_message_by_view(
            message=message_or_callback_query.message,
            view=view,
        )
    await state.finish()


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_product_quantity_update_in_shopping_cart,
        CartProductQuantityUpdateCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_delete_all_cart_products_confirm,
        Text('user-shopping-cart-delete-all-confirm'),
        chat_type=ChatType.PRIVATE,
        state=UserShoppingCartDeleteAllStates.confirm,
    )
    dispatcher.register_callback_query_handler(
        on_delete_all_cart_products_in_shopping_cart,
        Text('ask-for-delete-all-in-shopping-cart'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_delete_cart_product_in_shopping_cart,
        CartProductDeleteCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_show_shopping_cart,
        Text('show-user-shopping-cart'),
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
