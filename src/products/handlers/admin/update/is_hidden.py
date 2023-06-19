from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.views import edit_message_by_view
from products.callback_data import AdminProductUpdateCallbackData
from products.repositories import ProductRepository
from products.views import AdminProductDetailView

__all__ = ('register_handlers',)


async def on_hidden_status_toggle(
        callback_query: CallbackQuery,
        callback_data: dict,
        product_repository: ProductRepository,
) -> None:
    product_id: int = callback_data['product_id']
    product = product_repository.get_by_id(product_id)
    is_hidden = not product.is_hidden
    product_repository.update_hidden_status(
        product_id=product_id,
        is_hidden=is_hidden,
    )
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    text = (
        f'❗️ Product has been hidden'
        if product.is_hidden
        else '❗️ Product is no more hidden'
    )
    await callback_query.answer(text)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_hidden_status_toggle,
        AdminProductUpdateCallbackData().filter(field='hidden-status'),
        state='*',
    )
