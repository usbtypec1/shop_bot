from aiogram.types import CallbackQuery

from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import CategoryDetailCallbackData
from loader import dp
from repositories.database import CategoryRepository, SubcategoryRepository
from services.db_api.session import session_factory
from views import edit_message_by_view, CategoryDetailView


@dp.callback_query_handler(
    CategoryDetailCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_show_category_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    category_id: int = callback_data['category_id']
    category_repository = CategoryRepository(session_factory)
    subcategory_repository = SubcategoryRepository(session_factory)
    category = category_repository.get_by_id(category_id)
    subcategories = subcategory_repository.get_by_category_id(category_id)
    view = CategoryDetailView(category=category, subcategories=subcategories)
    await edit_message_by_view(message=callback_query.message, view=view)
