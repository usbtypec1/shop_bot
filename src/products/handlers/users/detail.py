from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from products.callback_data import UserProductDetailCallbackData

__all__ = ('register_handlers',)

from products.repositories import ProductRepository


async def on_show_product_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        product_repository: ProductRepository,
) -> None:
    product_id: int = callback_data['product_id']
    product = product_repository.get_by_id(product_id)
    if not product.can_be_purchased:
        await callback_query.answer('Coming soon...', show_alert=True)
        return


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_product_detail,
        UserProductDetailCallbackData().filter(),
        state='*',
    )
