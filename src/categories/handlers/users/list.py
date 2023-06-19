from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ChatType, Message

from categories.repositories import CategoryRepository
from categories.views import UserCategoryListView
from common.views import answer_view


async def on_show_categories_list(
        message: Message,
        state: FSMContext,
        category_repository: CategoryRepository,
) -> None:
    await state.finish()
    categories = category_repository.get_categories()
    view = UserCategoryListView(categories)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_categories_list,
        Text('🛒 Products'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
