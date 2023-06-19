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


async def on_start_max_displayed_stock_count_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductUpdateStates.max_displayed_stock.set()
    await state.update_data(product_id=product_id)
    await callback_query.message.answer(
        'Provide new maximum displayed stock count')


async def on_max_displayed_stock_count_input(
        message: Message,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    try:
        max_displayed_stock_count = int(message.text)
    except ValueError:
        await message.reply('❌ Invalid number')
        return

    state_data = await state.get_data()
    product_id: int = state_data['product_id']
    product_repository.update_max_displayed_stock_count(
        product_id=product_id,
        max_displayed_stock_count=max_displayed_stock_count
    )
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    await message.answer('✅ Maximum displayed stock count has been updated')
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_max_displayed_stock_count_update_flow,
        AdminProductUpdateCallbackData().filter(field='max-displayed-stock'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_max_displayed_stock_count_input,
        content_types=ContentType.TEXT,
        state=ProductUpdateStates.max_displayed_stock,
    )
