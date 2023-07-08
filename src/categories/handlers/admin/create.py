import structlog
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ContentType,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from emoji import is_emoji

from categories.callback_data import CategoryCreateCallbackData
from categories.repositories import CategoryRepository
from categories.states import CategoryCreateStates
from categories.views import CategoryListView, CategoryDetailView
from common.filters import AdminFilter
from common.views import answer_view

__all__ = ('register_handlers',)

logger = structlog.get_logger('app')


async def on_start_category_creation_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    parent_id: int | None = callback_data['parent_id']
    await CategoryCreateStates.name.set()
    await state.update_data(parent_id=parent_id)
    await callback_query.message.answer('✏️ Enter the title')
    logger.debug('Create category: start creation flow')


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


async def on_category_icon_input(
        message: Message,
        state: FSMContext,
) -> None:
    icon = message.text if is_emoji(message.text) else None
    await state.update_data(icon=icon)
    await CategoryCreateStates.priority.set()
    await message.answer(text='Enter Category/Subcategory Priority')
    logger.debug('Create category: step 2 - input icon', icon=icon)


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


async def on_hidden_option_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    is_hidden = callback_query.data == 'category-is-hidden'
    await state.update_data(is_hidden=is_hidden)
    await CategoryCreateStates.can_be_seen.set()
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton('Yes', callback_data='category-can-not-be-seen'),
        InlineKeyboardButton('No', callback_data='category-can-be-seen'),
    )
    await callback_query.message.answer(
        text='Prevent Users from seeing this category/subcategory?',
        reply_markup=markup,
    )
    logger.debug(
        'Create category: step 5 - choose hidden option',
        is_hidden=is_hidden,
    )


async def on_can_be_seen_option_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
        category_repository: CategoryRepository,
) -> None:
    can_be_seen = callback_query.data == 'category-can-be-seen'
    state_data = await state.get_data()
    await state.finish()
    logger.debug(
        'Create category: step 6 - choose can_be_seen option',
        can_be_seen=can_be_seen,
    )

    parent_id: int | None = state_data['parent_id']

    category_repository.create(
        name=state_data['name'],
        icon=state_data['icon'],
        priority=state_data['priority'],
        max_displayed_stock_count=state_data['max_displayed_stocks_count'],
        is_hidden=state_data['is_hidden'],
        can_be_seen=can_be_seen,
        parent_id=parent_id,
    )

    if parent_id is None:
        categories = category_repository.get_categories()
        view = CategoryListView(categories)
    else:
        parent_category = category_repository.get_by_id(parent_id)
        subcategories = category_repository.get_categories(parent_id)
        view = CategoryDetailView(
            category=parent_category,
            subcategories=subcategories,
        )

    await callback_query.message.answer(
        '✅ New category/subcategory has been created',
    )
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_category_creation_flow,
        CategoryCreateCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_category_name_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=CategoryCreateStates.name,
    )
    dispatcher.register_message_handler(
        on_category_icon_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=CategoryCreateStates.icon,
    )
    dispatcher.register_message_handler(
        on_category_priority_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=CategoryCreateStates.priority,
    )
    dispatcher.register_message_handler(
        on_max_displayed_stocks_count_choice,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=CategoryCreateStates.max_displayed_stocks_count,
    )
    dispatcher.register_callback_query_handler(
        on_hidden_option_choice,
        AdminFilter(),
        state=CategoryCreateStates.is_hidden,
    )
    dispatcher.register_callback_query_handler(
        on_can_be_seen_option_choice,
        AdminFilter(),
        state=CategoryCreateStates.can_be_seen,
    )
