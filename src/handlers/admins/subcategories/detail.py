from aiogram.types import CallbackQuery

from keyboards.inline.callback_factories import SubcategoryDetailCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from database.session import session_factory
from views import SubcategoryDetailView, edit_message_by_view


@dp.callback_query_handler(
    SubcategoryDetailCallbackData().filter(),
    state='*',
)
async def on_show_subcategory_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    subcategory_id: int = callback_data['subcategory_id']
    subcategory_repository = SubcategoryRepository(session_factory)
    subcategory = subcategory_repository.get_by_id(subcategory_id)
    view = SubcategoryDetailView(subcategory)
    await edit_message_by_view(message=callback_query.message, view=view)
