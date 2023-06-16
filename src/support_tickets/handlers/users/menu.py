from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.views import answer_view
from support_tickets.views import UserSupportMenuView


async def on_show_support_menu(
        message: Message,
) -> None:
    view = UserSupportMenuView()
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_support_menu,
        Text('👨‍💻 Support'),
        state='*',
    )
