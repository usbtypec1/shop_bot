from aiogram import Dispatcher
from aiogram.types import CallbackQuery

import config
from products.callback_data import UserProductDetailCallbackData
from products.repositories import ProductRepository
from products.services import answer_view_with_media
from products.views import UserProductDetailView
from users.repositories import UserRepository

__all__ = ('register_handlers',)


async def on_show_product_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        product_repository: ProductRepository,
        user_repository: UserRepository,
) -> None:
    user = user_repository.get_by_telegram_id(callback_query.from_user.id)
    product_id: int = callback_data['product_id']
    product = product_repository.get_by_id(product_id)
    if not product.can_be_purchased:
        await callback_query.answer('Coming soon...', show_alert=True)
        return
    view = UserProductDetailView(
        product=product,
        permanent_discount=user.permanent_discount,
    )
    await answer_view_with_media(
        view=view,
        message=callback_query.message,
        base_path=config.MEDIA_FILES_PATH,
        product=product,
    )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_product_detail,
        UserProductDetailCallbackData().filter(),
        state='*',
    )
