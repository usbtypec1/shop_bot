from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ChatType, Message, CallbackQuery

from categories.repositories import CategoryRepository
from categories.views import UserCategoryListView
from common.views import answer_view, edit_message_by_view


async def on_show_categories_list(
        message_or_query: Message | CallbackQuery,
        state: FSMContext,
        category_repository: CategoryRepository,
) -> None:
    await state.finish()
    categories = category_repository.get_categories()
    view = UserCategoryListView(categories)
    if isinstance(message_or_query, CallbackQuery):
        await edit_message_by_view(message=message_or_query.message, view=view)
    else:
        await answer_view(message=message_or_query, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_categories_list,
        Text('show-top-level-categories-list'),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_categories_list,
        Text('🛒 Products'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
