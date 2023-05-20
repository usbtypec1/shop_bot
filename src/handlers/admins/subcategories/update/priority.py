from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from keyboards.inline.callback_factories import SubcategoryUpdateCallbackData
from loader import dp
from repositories.database import SubcategoryRepository
from services.db_api.session import session_factory
from states.category_states import SubcategoryUpdateStates
from views import SubcategoryDetailView, answer_view


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
):
    if not message.text.isdigit():
        await message.answer('Priority must be a number')
        return

    state_data = await state.get_data()
    await state.finish()

    subcategory_id: int = state_data['subcategory_id']
    priority = int(message.text)

    subcategory_repository = SubcategoryRepository(session_factory)
    subcategory_repository.update_priority(
        subcategory_id=subcategory_id,
        subcategory_priority=priority,
    )
    subcategory = subcategory_repository.get_by_id(subcategory_id)

    view = SubcategoryDetailView(subcategory)
    await answer_view(message=message, view=view)
