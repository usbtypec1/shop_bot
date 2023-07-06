from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from categories.callback_data import UserCategoryDetailCallbackData
from categories.repositories import CategoryRepository
from categories.views import UserCategoryDetailView
from common.views import edit_message_by_view
from products.repositories import ProductRepository


async def on_show_category_detail(
        callback_query: CallbackQuery,
        state: FSMContext,
        callback_data: dict,
        category_repository: CategoryRepository,
        product_repository: ProductRepository,
) -> None:
    await state.finish()
    category_id: int = callback_data['category_id']
    category = category_repository.get_by_id(category_id)

    if not category.can_be_seen:
        await callback_query.answer('Coming soon...', show_alert=True)
        return

    subcategories = category_repository.get_categories(parent_id=category_id)
    products = product_repository.get_by_category_id(category_id)
    view = UserCategoryDetailView(
        subcategories=subcategories,
        products=products,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_category_detail,
        UserCategoryDetailCallbackData().filter(),
        state='*',
    )
