from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from categories.callback_data import SubcategoryUpdateCallbackData
from categories.repositories import CategoryRepository
from categories.states import SubcategoryUpdateStates
from categories.views import SubcategoryDetailView
from common.views import answer_view
from loader import dp


@dp.callback_query_handler(
    SubcategoryUpdateCallbackData().filter(field='name'),
    state='*',
)
async def on_start_subcategory_name_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    subcategory_id: int = callback_data['subcategory_id']
    await SubcategoryUpdateStates.name.set()
    await state.update_data(subcategory_id=subcategory_id)
    await callback_query.message.edit_text('Provide new title')


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=SubcategoryUpdateStates.name,
)
async def on_subcategory_name_input(
        message: Message,
        state: FSMContext,
        category_repository: CategoryRepository,
):
    state_data = await state.get_data()
    await state.finish()

    category_id: int = state_data['subcategory_id']
    category_name = message.text

    category_repository.update_name(
        category_id=category_id,
        category_name=category_name,
    )
    category = category_repository.get_by_id(category_id)

    view = SubcategoryDetailView(category)
    await answer_view(message=message, view=view)
