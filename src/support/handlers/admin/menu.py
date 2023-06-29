from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.filters import AdminFilter
from common.views import answer_view
from support.views import AdminSupportMenuView


async def on_show_support_menu(
        message: Message,
) -> None:
    view = AdminSupportMenuView()
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_support_menu,
        Text('👨‍💻 Support'),
        AdminFilter(),
        state='*',
    )
