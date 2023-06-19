from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.views import edit_message_by_view
from products.callback_data import AdminProductUpdateCallbackData
from products.repositories import ProductRepository
from products.views import AdminProductDetailView

__all__ = ('register_handlers',)


async def on_duplicated_stock_entries_status_toggle(
        callback_query: CallbackQuery,
        callback_data: dict,
        product_repository: ProductRepository,
) -> None:
    product_id: int = callback_data['product_id']
    product = product_repository.get_by_id(product_id)
    is_duplicated_stock_entries_allowed = (
        not product.is_duplicated_stock_entries_allowed
    )
    product_repository.update_duplicated_stock_entries_status(
        product_id=product_id,
        is_duplicated_stock_entries_allowed=is_duplicated_stock_entries_allowed,
    )
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    text = (
        f'❗️ Product duplicated entries have been allowed'
        if product.is_duplicated_stock_entries_allowed
        else '❗️ Product duplicated entries have been prevented'
    )
    await callback_query.answer(text)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_duplicated_stock_entries_status_toggle,
        AdminProductUpdateCallbackData().filter(
            field='duplicated-entries-status',
        ),
        state='*',
    )
