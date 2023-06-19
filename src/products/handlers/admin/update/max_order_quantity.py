from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ContentType

from common.filters import AdminFilter
from common.views import answer_view
from products.callback_data import AdminProductUpdateCallbackData
from products.repositories import ProductRepository
from products.states import ProductUpdateStates
from products.views import AdminProductDetailView

__all__ = ('register_handlers',)


async def on_start_max_order_quantity_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductUpdateStates.max_order_quantity.set()
    await state.update_data(product_id=product_id)
    await callback_query.message.answer('Provide new maximum order quantity')


async def on_max_order_quantity_input(
        message: Message,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    try:
        max_order_quantity = int(message.text)
    except ValueError:
        await message.reply('❌ Invalid quantity (must be a number)!')
        return

    state_data = await state.get_data()
    product_id: int = state_data['product_id']
    product_repository.update_max_order_quantity(
        product_id=product_id,
        max_order_quantity=max_order_quantity,
    )
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    await message.answer('✅ Maximum order quantity has been updated')
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_max_order_quantity_update_flow,
        AdminProductUpdateCallbackData().filter(field='max-order-quantity'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_max_order_quantity_input,
        content_types=ContentType.TEXT,
        state=ProductUpdateStates.max_order_quantity,
    )
