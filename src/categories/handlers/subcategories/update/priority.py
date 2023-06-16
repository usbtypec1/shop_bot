from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from categories.callback_data import SubcategoryUpdateCallbackData
from categories.repositories import CategoryRepository
from categories.states import SubcategoryUpdateStates
from categories.views import SubcategoryDetailView
from common.views import answer_view
from loader import dp


@dp.callback_query_handler(
    SubcategoryUpdateCallbackData().filter(field='priority'),
    state='*',
)
async def on_start_subcategory_priority_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    subcategory_id: int = callback_data['subcategory_id']
    await SubcategoryUpdateStates.priority.set()
    await state.update_data(subcategory_id=subcategory_id)
    await callback_query.message.edit_text('Provide priority value')


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=SubcategoryUpdateStates.priority,
)
async def on_category_priority_input(
        message: Message,
        state: FSMContext,
        category_repository: CategoryRepository,
):
    if not message.text.isdigit():
        await message.answer('Priority must be a number')
        return

    state_data = await state.get_data()
    await state.finish()

    subcategory_id: int = state_data['subcategory_id']
    priority = int(message.text)

    category_repository.update_priority(
        category_id=subcategory_id,
        category_priority=priority,
    )
    subcategory = category_repository.get_by_id(subcategory_id)

    view = SubcategoryDetailView(subcategory)
    await answer_view(message=message, view=view)
