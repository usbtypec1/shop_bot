from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery
from aiogram.types import Message

from categories.callback_data import SubcategoryListCallbackData
from categories.repositories import CategoryRepository
from categories.views import CategoryListView
from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view

__all__ = ('register_handlers',)


async def on_show_categories_list(
        message: Message,
        category_repository: CategoryRepository,
) -> None:
    categories = category_repository.get_categories()
    view = CategoryListView(categories)
    await answer_view(message=message, view=view)


async def on_show_subcategories_list(
        callback_query: CallbackQuery,
        callback_data: dict,
        category_repository: CategoryRepository,
) -> None:
    category_id: int = callback_data['category_id']
    subcategories = category_repository.get_subcategories(category_id)
    view = CategoryListView(
        categories=subcategories,
        parent_id=category_id,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_categories_list,
        Text('📁 Categories Control'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_show_subcategories_list,
        SubcategoryListCallbackData().filter(),
        state='*',
    )
