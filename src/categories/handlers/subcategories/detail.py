from aiogram.types import CallbackQuery

from categories.callback_data import SubcategoryDetailCallbackData
from categories.repositories import CategoryRepository
from categories.views import SubcategoryDetailView
from common.views import edit_message_by_view
from loader import dp


@dp.callback_query_handler(
    SubcategoryDetailCallbackData().filter(),
    state='*',
)
async def on_show_subcategory_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        category_repository: CategoryRepository,
) -> None:
    subcategory_id: int = callback_data['subcategory_id']
    subcategory = category_repository.get_by_id(subcategory_id)
    view = SubcategoryDetailView(subcategory)
    await edit_message_by_view(message=callback_query.message, view=view)
