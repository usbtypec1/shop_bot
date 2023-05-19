import structlog
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ContentType,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from emoji import is_emoji

from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import CategoriesCallbackFactory
from loader import dp
from repositories.database import CategoryRepository, SubcategoryRepository
from responses.category_management import (
    CategoriesResponse
)
from services.db_api.queries import add_category, get_all_categories
from services.db_api.session import session_factory
from states.category_states import CategoryCreateStates
from views import CategoryDetailView, CategoryListView, answer_view

logger = structlog.get_logger('app')


@dp.callback_query_handler(
    CategoriesCallbackFactory().filter(action='add'),
    IsUserAdmin(),
    state='*',
)
async def on_start_category_creation_flow(
        callback_query: CallbackQuery
) -> None:
    await CategoryCreateStates.name.set()
    await callback_query.message.answer('✏️ Enter the title')
    logger.debug('Create category: start creation flow')


@dp.message_handler(
    IsUserAdmin(),
    content_types=ContentType.TEXT,
    state=CategoryCreateStates.name,
)
async def on_category_name_input(
        message: Message,
        state: FSMContext,
) -> None:
    await state.update_data(name=message.text)
    await CategoryCreateStates.icon.set()
    await message.answer(
        text='Enter Category/Subcategory Icon (Enter any A-Z text to skip)'
    )
    logger.debug('Create category: step 1 - input name', name=message.text)


@dp.message_handler(
    IsUserAdmin(),
    content_types=ContentType.TEXT,
    state=CategoryCreateStates.icon,
)
async def on_category_icon_input(
        message: Message,
        state: FSMContext,
) -> None:
    icon = message.text if is_emoji(message.text) else None
    await state.update_data(icon=icon)
    await CategoryCreateStates.priority.set()
    await message.answer(text='Enter Category/Subcategory Priority')
    logger.debug('Create category: step 2 - input icon', icon=icon)


@dp.message_handler(
    IsUserAdmin(),
    content_types=ContentType.TEXT,
    state=CategoryCreateStates.priority,
)
async def on_category_priority_input(
        message: Message,
        state: FSMContext,
) -> None:
    if not message.text.isdigit():
        await message.answer('Priority must be a number')
        return
    priority = int(message.text)
    await state.update_data(priority=priority)
    await CategoryCreateStates.max_displayed_stocks_count.set()
    markup = InlineKeyboardMarkup()
    await message.answer(
        text='Maximum Displayed Stock',
        reply_markup=markup,
    )
    logger.debug('Create category: step 3 - input priority', priority=priority)


@dp.message_handler(
    IsUserAdmin(),
    content_types=ContentType.TEXT,
    state=CategoryCreateStates.max_displayed_stocks_count,
)
async def on_max_displayed_stocks_count_choice(
        message: Message,
        state: FSMContext,
) -> None:
    if not message.text.isdigit():
        await message.reply('It must be number')
        return
    max_displayed_stocks_count = int(message.text)
    await state.update_data(
        max_displayed_stocks_count=max_displayed_stocks_count,
    )
    await CategoryCreateStates.is_hidden.set()
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='category-is-hidden'),
        InlineKeyboardButton('No', callback_data='category-is-not-hidden'),
    )
    await message.answer(
        text='Hide this category?',
        reply_markup=markup,
    )
    logger.debug(
        'Create category: step 4 - choose stocks display option',
        max_displayed_stocks_count=max_displayed_stocks_count,
    )


@dp.callback_query_handler(
    IsUserAdmin(),
    state=CategoryCreateStates.is_hidden,
)
async def on_hidden_option_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    is_hidden = callback_query.data == 'category-is-hidden'
    await state.update_data(is_hidden=is_hidden)
    await CategoryCreateStates.can_be_seen.set()
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='category-can-be-seen'),
        InlineKeyboardButton('No', callback_data='category-can-not-be-seen'),
    )
    await callback_query.message.answer(
        text='Prevent Users from seeing this category/subcategory?',
        reply_markup=markup,
    )
    logger.debug(
        'Create category: step 5 - choose hidden option',
        is_hidden=is_hidden,
    )


@dp.callback_query_handler(
    IsUserAdmin(),
    state=CategoryCreateStates.can_be_seen,
)
async def on_can_be_seen_option_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    can_be_seen = callback_query.data == 'category-can-be-seen'
    state_data = await state.get_data()
    await state.finish()
    logger.debug(
        'Create category: step 6 - choose can_be_seen option',
        can_be_seen=can_be_seen,
    )

    category_repository = CategoryRepository(session_factory)
    category_repository.create(
        name=state_data['name'],
        icon=state_data['icon'],
        priority=state_data['priority'],
        max_displayed_stock_count=state_data['max_displayed_stocks_count'],
        is_hidden=state_data['is_hidden'],
        can_be_seen=can_be_seen,
    )
    categories = category_repository.get_all()
    view = CategoryListView(categories)
    await callback_query.message.answer('✅ New category has been created')
    await answer_view(message=callback_query.message, view=view)
