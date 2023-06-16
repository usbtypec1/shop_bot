from aiogram.types import CallbackQuery

from categories.callback_data import SubcategoryUpdateCallbackData
from categories.repositories import CategoryRepository
from categories.views import SubcategoryDetailView
from common.views import edit_message_by_view
from database.session import session_factory
from loader import dp


@dp.callback_query_handler(
    SubcategoryUpdateCallbackData().filter(field='can-be-seen-status'),
    state='*',
)
async def on_start_can_be_seen_status_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
):
    subcategory_id: int = callback_data['subcategory_id']
    subcategory_repository = CategoryRepository(session_factory)
    subcategory = subcategory_repository.get_by_id(subcategory_id)
    subcategory_repository.update_can_be_seen_status(
        category_id=subcategory.id,
        can_be_seen=not subcategory.can_be_seen,
    )
    subcategory = subcategory_repository.get_by_id(subcategory_id)
    view = SubcategoryDetailView(subcategory)
    await edit_message_by_view(message=callback_query.message, view=view)
