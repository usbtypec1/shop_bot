from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from filters.is_admin import IsUserAdmin
from loader import dp
from repositories.database import CategoryRepository
from database.session import session_factory
from views import CategoryListView, answer_view


@dp.message_handler(
    Text('📁 Categories Control'),
    IsUserAdmin(),
    state='*',
)
async def on_show_categories_list(
        message: Message,
) -> None:
    category_repository = CategoryRepository(session_factory)
    categories = category_repository.get_all()
    view = CategoryListView(categories)
    await answer_view(message=message, view=view)
