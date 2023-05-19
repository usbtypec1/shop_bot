from aiogram.dispatcher import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from keyboards.inline.callback_factories import CategoryUpdateCallbackData
from loader import dp
from repositories.database import CategoryRepository, SubcategoryRepository
from responses.category_management import CategoryMenuResponse
from services.db_api.session import session_factory
from states.category_states import CategoryUpdateStates


@dp.callback_query_handler(
    CategoryUpdateCallbackData().filter(field='can-be-seen-status'),
    state='*',
)
async def on_start_can_be_seen_status_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    category_id: int = callback_data['category_id']
    await CategoryUpdateStates.can_be_seen.set()
    await state.update_data(category_id=category_id)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='category-can-not-be-seen'),
        InlineKeyboardButton('No', callback_data='category-can-be-seen'),
    )
    await callback_query.message.answer(
        text='Prevent Users from seeing this category/subcategory?',
        reply_markup=markup,
    )


@dp.callback_query_handler(
    state=CategoryUpdateStates.can_be_seen,
)
async def on_category_can_be_seen_status_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
):
    state_data = await state.get_data()
    await state.finish()

    category_id: int = state_data['category_id']
    can_be_seen = callback_query.data == 'category-can-be-seen'

    category_repository = CategoryRepository(session_factory)
    subcategory_repository = SubcategoryRepository(session_factory)

    category_repository.update_can_be_seen_status(
        category_id=category_id,
        can_be_seen=can_be_seen,
    )
    category = category_repository.get_by_id(category_id)
    subcategories = subcategory_repository.get_by_category_id(category_id)

    await CategoryMenuResponse(
        update=callback_query,
        category_id=category_id,
        category_name=category.name,
        subcategories=subcategories
    )
