from aiogram.types import CallbackQuery

from keyboards.inline.callback_factories import SubcategoryUpdateCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from services.db_api.session import session_factory
from views import SubcategoryDetailView, edit_message_by_view


@dp.callback_query_handler(
    SubcategoryUpdateCallbackData().filter(field='can-be-seen-status'),
    state='*',
)
async def on_start_can_be_seen_status_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
):
    subcategory_id: int = callback_data['subcategory_id']
    subcategory_repository = SubcategoryRepository(session_factory)
    subcategory = subcategory_repository.get_by_id(subcategory_id)
    subcategory_repository.update_can_be_seen_status(
        subcategory_id=subcategory.id,
        can_be_seen=not subcategory.can_be_seen,
    )
    subcategory = subcategory_repository.get_by_id(subcategory_id)
    view = SubcategoryDetailView(subcategory)
    await edit_message_by_view(message=callback_query.message, view=view)
