from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from categories.repositories import CategoryRepository
from categories.views import CategoryDetailView
from common.views import edit_message_by_view
from categories.callback_data import CategoryUpdateCallbackData

__all__ = ('register_handlers',)


async def on_start_is_hidden_status_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        category_repository: CategoryRepository,
):
    category_id: int = callback_data['category_id']
    category = category_repository.get_by_id(category_id)
    category_repository.update_hidden_status(
        category_id=category_id,
        is_hidden=not category.is_hidden,
    )
    category = category_repository.get_by_id(category_id)
    subcategories = category_repository.get_subcategories(parent_id=category_id)
    view = CategoryDetailView(category=category, subcategories=subcategories)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_is_hidden_status_update_flow,
        CategoryUpdateCallbackData().filter(field='hidden-status'),
        state='*',
    )
