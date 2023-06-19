from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType

from common.views import answer_view
from products.callback_data import AdminProductUpdateCallbackData
from products.repositories import ProductRepository
from products.states import ProductUpdateStates
from products.views import AdminProductDetailView

__all__ = ('register_handlers',)


async def on_start_product_name_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductUpdateStates.name.set()
    await state.update_data(product_id=product_id)
    await callback_query.message.answer('Provide new name')


async def on_product_name_input(
        message: Message,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    state_data = await state.get_data()
    product_id: int = state_data['product_id']
    name = message.text
    product_repository.update_name(product_id=product_id, name=name)
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    await message.answer('✅ Product name has been updated')
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_product_name_update_flow,
        AdminProductUpdateCallbackData().filter(field='name'),
        state='*',
    )
    dispatcher.register_message_handler(
        on_product_name_input,
        content_types=ContentType.TEXT,
        state=ProductUpdateStates.name,
    )
