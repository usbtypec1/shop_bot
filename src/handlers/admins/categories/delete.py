from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import CategoryDeleteCallbackData
from loader import dp
from repositories.database import CategoryRepository
from services.db_api.session import session_factory
from states.category_states import CategoryDeleteStates
from views import edit_message_by_view, CategoryAskDeleteConfirmationView


@dp.callback_query_handler(
    CategoryDeleteCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_ask_delete_category_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
) -> None:
    category_id: int = callback_data['category_id']
    await CategoryDeleteStates.confirm.set()
    await state.update_data(category_id=category_id)
    view = CategoryAskDeleteConfirmationView(category_id)
    await edit_message_by_view(message=callback_query.message, view=view)


@dp.callback_query_handler(
    IsUserAdmin(),
    Text('category-delete-confirm'),
    state=CategoryDeleteStates.confirm,
)
async def on_delete_category_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    category_id: int = state_data['category_id']
    await state.finish()
    category_repository = CategoryRepository(session_factory)
    category_repository.delete_by_id(category_id)
    await callback_query.message.edit_text('Category has been deleted')
