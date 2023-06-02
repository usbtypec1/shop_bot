from aiogram.types import CallbackQuery

from keyboards.inline.callback_factories import SubcategoryListCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from database.session import session_factory
from views import SubcategoryListView, edit_message_by_view


@dp.callback_query_handler(
    SubcategoryListCallbackData().filter(),
    state='*',
)
async def on_show_subcategories_list(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    category_id: int = callback_data['category_id']
    subcategory_repository = SubcategoryRepository(session_factory)
    subcategories = subcategory_repository.get_by_category_id(category_id)
    view = SubcategoryListView(
        subcategories=subcategories,
        category_id=category_id,
    )
    await edit_message_by_view(message=callback_query.message, view=view)
