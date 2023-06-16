from aiogram.types import CallbackQuery

from categories.callback_data import SubcategoryUpdateCallbackData
from categories.repositories import CategoryRepository
from categories.views import SubcategoryDetailView
from common.views import edit_message_by_view
from loader import dp


@dp.callback_query_handler(
    SubcategoryUpdateCallbackData().filter(field='hidden-status'),
    state='*',
)
async def on_hidden_status_switch(
        callback_query: CallbackQuery,
        callback_data: dict,
        category_repository: CategoryRepository,
):
    subcategory_id: int = callback_data['subcategory_id']
    subcategory = category_repository.get_by_id(subcategory_id)
    category_repository.update_hidden_status(
        category_id=subcategory.id,
        is_hidden=not subcategory.is_hidden,
    )
    subcategory = category_repository.get_by_id(subcategory_id)
    view = SubcategoryDetailView(subcategory)
    await edit_message_by_view(message=callback_query.message, view=view)
