from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import SubcategoryDeleteCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from services.db_api.session import session_factory
from states.category_states import SubcategoryDeleteStates
from views import SubcategoryAskDeleteConfirmationView, edit_message_by_view


@dp.callback_query_handler(
    SubcategoryDeleteCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_ask_delete_subcategory_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    subcategory_id: int = callback_data['subcategory_id']
    await SubcategoryDeleteStates.confirm.set()
    await state.update_data(subcategory_id=subcategory_id)
    view = SubcategoryAskDeleteConfirmationView(subcategory_id)
    await edit_message_by_view(message=callback_query.message, view=view)


@dp.callback_query_handler(
    IsUserAdmin(),
    state=SubcategoryDeleteStates.confirm,
)
async def on_delete_subcategory_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    subcategory_id: int = state_data['subcategory_id']
    subcategory_repository = SubcategoryRepository(session_factory)
    subcategory_repository.delete_by_id(subcategory_id)
    await callback_query.message.edit_text('Subcategory has been deleted')
