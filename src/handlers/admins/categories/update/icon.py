from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ContentType, Message
from emoji import is_emoji

from keyboards.inline.callback_factories import CategoryUpdateCallbackData
from loader import dp
from repositories.database import CategoryRepository, SubcategoryRepository
from database.session import session_factory
from states.category_states import CategoryUpdateStates
from views import answer_view, CategoryDetailView


@dp.callback_query_handler(
    CategoryUpdateCallbackData().filter(field='icon'),
    state='*',
)
async def on_start_category_icon_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    category_id: int = callback_data['category_id']
    await CategoryUpdateStates.icon.set()
    await state.update_data(category_id=category_id)
    await callback_query.message.answer(
        'Provide new icon (Enter any A-Z text to delete)'
    )


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=CategoryUpdateStates.icon,
)
async def on_category_icon_input(
        message: Message,
        state: FSMContext,
):
    state_data = await state.get_data()
    await state.finish()

    category_id: int = state_data['category_id']
    category_icon = message.text if is_emoji(message.text) else None

    category_repository = CategoryRepository(session_factory)
    subcategory_repository = SubcategoryRepository(session_factory)

    category_repository.update_icon(
        category_id=category_id,
        category_icon=category_icon,
    )
    category = category_repository.get_by_id(category_id)
    subcategories = subcategory_repository.get_by_category_id(category_id)

    view = CategoryDetailView(category=category, subcategories=subcategories)
    await answer_view(message=message, view=view)
