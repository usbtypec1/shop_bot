from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.views import edit_message_by_view
from products.callback_data import AdminProductUpdateCallbackData
from products.repositories import ProductRepository
from products.views import AdminProductDetailView

__all__ = ('register_handlers',)


async def on_can_be_purchased_status_toggle(
        callback_query: CallbackQuery,
        callback_data: dict,
        product_repository: ProductRepository,
) -> None:
    product_id: int = callback_data['product_id']
    product = product_repository.get_by_id(product_id)
    can_be_purchased = not product.can_be_purchased
    product_repository.update_can_be_purchased_status(
        product_id=product_id,
        can_be_purchased=can_be_purchased,
    )
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    text = (
        f'❗️ Product purchases have been allowed'
        if product.can_be_purchased
        else '❗️ Product purchases have been prevented'
    )
    await callback_query.answer(text)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_can_be_purchased_status_toggle,
        AdminProductUpdateCallbackData().filter(
            field='can-be-purchased-status',
        ),
        state='*',
    )
