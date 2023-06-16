from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from categories.repositories import CategoryRepository
from categories.views import CategoryListView
from common.filters import AdminFilter
from common.views import answer_view

__all__ = ('register_handlers',)


async def on_show_categories_list(
        message: Message,
        category_repository: CategoryRepository,
) -> None:
    categories = category_repository.get_categories()
    view = CategoryListView(categories)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_categories_list,
        Text('📁 Categories Control'),
        AdminFilter(),
        state='*',
    )
