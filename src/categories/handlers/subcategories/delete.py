from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from categories.callback_data import SubcategoryDeleteCallbackData
from categories.repositories import CategoryRepository
from categories.states import SubcategoryDeleteStates
from categories.views import SubcategoryAskDeleteConfirmationView
from common.filters import AdminFilter
from common.views import edit_message_by_view
from loader import dp


@dp.callback_query_handler(
    SubcategoryDeleteCallbackData().filter(),
    AdminFilter(),
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
    AdminFilter(),
    state=SubcategoryDeleteStates.confirm,
)
async def on_delete_subcategory_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        category_repository: CategoryRepository,
) -> None:
    state_data = await state.get_data()
    subcategory_id: int = state_data['subcategory_id']
    category_repository.delete_by_id(subcategory_id)
    await callback_query.message.edit_text('Subcategory has been deleted')
