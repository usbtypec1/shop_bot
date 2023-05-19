import structlog
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
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
from responses.category_management import (
    CategoryMenuResponse,
    CategoriesResponse
)
from services.db_api import create_session
from services.db_api.queries import add_category, get_all_categories
from services.db_api.session import session_factory
from states.category_states import CategoryCreateStates

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
    await CategoryCreateStates.are_stocks_displayed.set()
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='stocks-are-displayed'),
        InlineKeyboardButton('No', callback_data='stocks-are-not-displayed'),
    )
    await message.answer(
        text=(
            'Maximum Displayed Stock. Show the total number of products under'
            ' all subcategories or under that subcategory?'
        ),
        reply_markup=markup,
    )
    logger.debug('Create category: step 3 - input priority', priority=priority)


@dp.callback_query_handler(
    IsUserAdmin(),
    Text('stocks-are-displayed') | Text('stocks-are-not-displayed'),
    state=CategoryCreateStates.are_stocks_displayed,
)
async def on_stocks_displayed_option_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    are_stocks_displayed = callback_query.data == 'stocks-are-displayed'
    await state.update_data(are_stocks_displayed=are_stocks_displayed)
    await CategoryCreateStates.is_hidden.set()
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='category-is-hidden'),
        InlineKeyboardButton('No', callback_data='category-is-not-hidden'),
    )
    await callback_query.message.answer(
        text='Hide this category?',
        reply_markup=markup,
    )
    logger.debug(
        'Create category: step 4 - choose stocks display option',
        are_stocks_displayed=are_stocks_displayed,
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
    state_data = state_data | {'can_be_seen': can_be_seen}
    logger.debug(
        'Create category: step 6 - choose can_be_seen option',
        can_be_seen=can_be_seen,
    )

    with session_factory() as session:
        add_category(
            session=session,
            name=state_data['name'],
            icon=state_data['icon'],
            priority=state_data['priority'],
            are_stocks_displayed=state_data['are_stocks_displayed'],
            is_hidden=state_data['is_hidden'],
            can_be_seen=state_data['can_be_seen'],
        )
        categories = get_all_categories(session)
    await callback_query.message.answer('✅ New category have been created')
    await CategoriesResponse(
        update=callback_query.message,
        categories=categories,
    )