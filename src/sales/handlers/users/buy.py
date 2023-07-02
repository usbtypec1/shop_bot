from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ChatType, Message, Update, ContentType

from products.callback_data import UserProductBuyCallbackData
from products.exceptions import ProductQuantityValidationError
from products.services import parse_product_quantity
from products.states import ProductBuyStates

__all__ = ('register_handlers',)


async def on_product_quantity_validation_error(
        update: Update,
        exception: ProductQuantityValidationError,
) -> bool:
    if update.message is not None:
        await update.message.answer(str(exception))
    return True


async def on_start_buy_product_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductBuyStates.quantity.set()
    await state.update_data(product_id=product_id)
    await callback_query.message.answer('Enter number of pieces')


async def on_product_quantity_to_buy_input(
        message: Message,
        state: FSMContext,
) -> None:
    quantity = parse_product_quantity(message.text)
    print(quantity)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_product_quantity_validation_error,
        exception=ProductQuantityValidationError,
    )
    dispatcher.register_callback_query_handler(
        on_start_buy_product_flow,
        UserProductBuyCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_product_quantity_to_buy_input,
        chat_type=ChatType.PRIVATE,
        content_types=ContentType.TEXT,
        state=ProductBuyStates.quantity,
    )
