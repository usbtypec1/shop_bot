from aiogram.types import CallbackQuery

from keyboards.inline.callback_factories import CategoryUpdateCallbackData
from loader import dp
from repositories.database import CategoryRepository, SubcategoryRepository
from database.session import session_factory
from views import CategoryDetailView, edit_message_by_view


@dp.callback_query_handler(
    CategoryUpdateCallbackData().filter(field='hidden-status'),
    state='*',
)
async def on_start_is_hidden_status_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
):
    category_id: int = callback_data['category_id']
    category_repository = CategoryRepository(session_factory)
    subcategory_repository = SubcategoryRepository(session_factory)
    category = category_repository.get_by_id(category_id)
    category_repository.update_hidden_status(
        category_id=category_id,
        is_hidden=not category.is_hidden,
    )
    category = category_repository.get_by_id(category_id)
    subcategories = subcategory_repository.get_by_category_id(category_id)
    view = CategoryDetailView(category=category, subcategories=subcategories)
    await edit_message_by_view(message=callback_query.message, view=view)
