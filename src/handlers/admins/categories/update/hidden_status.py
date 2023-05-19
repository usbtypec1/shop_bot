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
    CategoryUpdateCallbackData().filter(field='hidden-status'),
    state='*',
)
async def on_start_is_hidden_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext
):
    category_id: int = callback_data['category_id']
    await CategoryUpdateStates.is_hidden.set()
    await state.update_data(category_id=category_id)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='category-is-hidden'),
        InlineKeyboardButton('No', callback_data='category-is-not-hidden'),
    )
    await callback_query.message.answer(
        text='Hide this category?',
        reply_markup=markup,
    )


@dp.callback_query_handler(
    state=CategoryUpdateStates.is_hidden,
)
async def on_category_hidden_status_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
):
    state_data = await state.get_data()
    await state.finish()

    category_id: int = state_data['category_id']
    is_hidden = callback_query.data == 'category-is-hidden'

    category_repository = CategoryRepository(session_factory)
    subcategory_repository = SubcategoryRepository(session_factory)

    category_repository.update_hidden_status(
        category_id=category_id,
        is_hidden=is_hidden,
    )
    category = category_repository.get_by_id(category_id)
    subcategories = subcategory_repository.get_by_category_id(category_id)

    await CategoryMenuResponse(
        update=callback_query,
        category_id=category_id,
        category_name=category.name,
        subcategories=subcategories
    )
