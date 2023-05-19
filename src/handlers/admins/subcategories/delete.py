from aiogram.types import CallbackQuery

from keyboards.inline.callback_factories import SubcategoryDeleteCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from services.db_api.session import session_factory


@dp.callback_query_handler(
    SubcategoryDeleteCallbackData().filter(),
    state='*',
)
async def on_delete_subcategory(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    subcategory_id: int = callback_data['subcategory_id']
    subcategory_repository = SubcategoryRepository(session_factory)
    subcategory_repository.delete_by_id(subcategory_id)
    await callback_query.message.edit_text('Subcategory has been deleted')
