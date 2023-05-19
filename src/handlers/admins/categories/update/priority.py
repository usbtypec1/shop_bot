from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message

from keyboards.inline.callback_factories import CategoryUpdateCallbackData
from loader import dp
from repositories.database import CategoryRepository, SubcategoryRepository
from responses.category_management import CategoryMenuResponse
from services.db_api.session import session_factory
from states.category_states import CategoryUpdateStates


@dp.callback_query_handler(
    CategoryUpdateCallbackData().filter(field='priority'),
    state='*',
)
async def on_start_category_priority_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    category_id: int = callback_data['category_id']
    await CategoryUpdateStates.priority.set()
    await state.update_data(category_id=category_id)
    await callback_query.message.answer('Provide priority value')


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=CategoryUpdateStates.priority,
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

    category_id: int = state_data['category_id']
    priority = int(message.text)

    category_repository = CategoryRepository(session_factory)
    subcategory_repository = SubcategoryRepository(session_factory)
    category_repository.update_priority(
        category_id=category_id,
        category_priority=priority,
    )
    category = category_repository.get_by_id(category_id)
    subcategories = subcategory_repository.get_by_category_id(category_id)

    await CategoryMenuResponse(
        update=message,
        category_id=category_id,
        category_name=category.name,
        subcategories=subcategories
    )
