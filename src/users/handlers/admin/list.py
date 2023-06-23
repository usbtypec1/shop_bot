from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.filters import AdminFilter
from common.views import answer_view
from users.repositories import UserRepository
from users.views import UsersView

__all__ = ('on_show_users_list',)


async def on_show_users_list(
        message: Message,
        user_repository: UserRepository,
) -> None:
    total_balance = user_repository.get_total_balance()
    page_size = 10
    users = user_repository.get_by_usernames_and_ids(
        limit=page_size,
        offset=0,
    )
    view = UsersView(
        users=users,
        total_balance=total_balance,
        page_size=page_size,
    )
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_users_list,
        Text('🙍‍♂ Users'),
        AdminFilter(),
        state='*',
    )
