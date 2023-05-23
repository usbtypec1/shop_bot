from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from loader import dp
from views import UserSupportMenuView, answer_view


@dp.message_handler(
    Text('👨‍💻 Support'),
    state='*',
)
async def on_show_support_menu(
        message: Message,
) -> None:
    view = UserSupportMenuView()
    await answer_view(message=message, view=view)
