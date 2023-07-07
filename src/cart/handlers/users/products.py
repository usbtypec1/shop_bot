from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType, Update

from cart.exceptions import (
    ProductQuantityOutOfRangeError,
    NotEnoughProductQuantityError,
)
from cart.repositories import CartRepository
from cart.services import validate_product_quantity_change
from cart.states import UserShoppingCartAddToCartStates
from cart.views import (
    ProductQuantityOutOfRangeWarningView,
    NotEnoughProductQuantityWarningView
)
from common.views import answer_view
from products.callback_data import UserProductAddToCartCallbackData
from products.repositories import ProductRepository
from users.repositories import UserRepository

__all__ = ('register_handlers',)


async def on_not_enough_product_quantity_error(
        update: Update,
        exception: NotEnoughProductQuantityError,
        product_repository: ProductRepository,
) -> bool:
    product = product_repository.get_by_id(product_id=exception.product_id)
    view = NotEnoughProductQuantityWarningView(product.quantity)
    if update.message is not None:
        await answer_view(message=update.message, view=view)
    else:
        await update.callback_query.answer(
            text=view.get_text(),
            show_alert=True,
        )
    return True


async def on_product_quantity_out_of_range_error(
        update: Update,
        exception: ProductQuantityOutOfRangeError,
        product_repository: ProductRepository,
) -> bool:
    product = product_repository.get_by_id(exception.product_id)
    view = ProductQuantityOutOfRangeWarningView(product)
    if update.message is not None:
        await answer_view(message=update.message, view=view)
    else:
        await update.callback_query.answer(
            text=view.get_text(),
            show_alert=True,
        )
    return True


async def on_add_product_to_cart(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await UserShoppingCartAddToCartStates.quantity.set()
    await state.update_data(product_id=product_id)
    await callback_query.message.answer('Enter number of pieces')


async def on_product_quantity_input(
        message: Message,
        state: FSMContext,
        user_repository: UserRepository,
        product_repository: ProductRepository,
        cart_repository: CartRepository,
) -> None:
    if not message.text.isdigit():
        await message.reply('❌ Invalid number of pieces!')
        return

    state_data = await state.get_data()
    await state.finish()
    product_id: int = state_data['product_id']
    quantity = int(message.text)
    product = product_repository.get_by_id(product_id)

    validate_product_quantity_change(
        product=product,
        cart_product_quantity=0,
        will_be_changed_to=quantity,
    )
    user = user_repository.get_by_telegram_id(message.from_user.id)
    cart_repository.create(
        user_id=user.id,
        product_id=product.id,
        quantity=quantity,
    )

    await message.answer(
        'The selected product is added to your shopping cart.'
        ' You can manage it from its button in the menu.'
    )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_not_enough_product_quantity_error,
        exception=NotEnoughProductQuantityError,
    )
    dispatcher.register_errors_handler(
        on_product_quantity_out_of_range_error,
        exception=ProductQuantityOutOfRangeError,
    )
    dispatcher.register_callback_query_handler(
        on_add_product_to_cart,
        UserProductAddToCartCallbackData().filter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_product_quantity_input,
        content_types=ContentType.TEXT,
        state=UserShoppingCartAddToCartStates.quantity,
    )
