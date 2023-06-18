from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from categories.repositories import CategoryRepository
from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from products.callback_data import AdminProductListCallbackData
from products.repositories import ProductRepository
from products.views import AdminProductListView


async def on_show_top_level_categories_list(
        message: Message,
        category_repository: CategoryRepository,
) -> None:
    categories = category_repository.get_categories()
    view = AdminProductListView(categories=categories)
    await answer_view(message=message, view=view)


async def on_show_category_products_list(
        callback_query: CallbackQuery,
        callback_data: dict,
        category_repository: CategoryRepository,
        product_repository: ProductRepository,
) -> None:
    parent_id: int = callback_data['parent_id']
    subcategories = category_repository.get_subcategories(parent_id)
    products = product_repository.get_by_category_id(parent_id)
    view = AdminProductListView(
        parent_id=parent_id,
        products=products,
        categories=subcategories,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_top_level_categories_list,
        Text('📝 Products Management'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_show_category_products_list,
        AdminProductListCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
