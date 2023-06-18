from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from common.filters import AdminFilter
from common.views import edit_message_by_view
from products.callback_data import AdminProductDetailCallbackData
from products.repositories import ProductRepository
from products.views import AdminProductDetailView


async def on_show_product_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    await state.finish()
    product_id: int = callback_data['product_id']
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_product_detail,
        AdminProductDetailCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
