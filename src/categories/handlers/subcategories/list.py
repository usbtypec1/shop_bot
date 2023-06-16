from aiogram.types import CallbackQuery

from categories.callback_data import SubcategoryListCallbackData
from categories.repositories import CategoryRepository
from categories.views import SubcategoryListView
from common.views import edit_message_by_view
from loader import dp


@dp.callback_query_handler(
    SubcategoryListCallbackData().filter(),
    state='*',
)
async def on_show_subcategories_list(
        callback_query: CallbackQuery,
        callback_data: dict,
        category_repository: CategoryRepository,
) -> None:
    category_id: int = callback_data['category_id']
    subcategories = category_repository.get_subcategories(category_id)
    view = SubcategoryListView(
        subcategories=subcategories,
        category_id=category_id,
    )
    await edit_message_by_view(message=callback_query.message, view=view)
