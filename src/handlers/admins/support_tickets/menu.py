from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from filters.is_admin import IsUserAdmin
from loader import dp
from views import AdminSupportMenuView, answer_view


@dp.message_handler(
    Text('👨‍💻 Support'),
    IsUserAdmin(),
    state='*',
)
async def on_show_support_menu(
        message: Message,
) -> None:
    view = AdminSupportMenuView()
    await answer_view(message=message, view=view)
