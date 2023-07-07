import contextlib

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from aiogram.utils.exceptions import MessageNotModified

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from users.repositories import UserRepository
from users.views import UserListView

__all__ = ('on_show_users_list',)


async def on_show_users_without_discount_list(
        callback_query: CallbackQuery,
        user_repository: UserRepository,
) -> None:
    total_balance = user_repository.get_total_balance()
    users = user_repository.get_without_permanent_discount()
    view = UserListView(users=users, total_balance=total_balance)
    with contextlib.suppress(MessageNotModified):
        await edit_message_by_view(message=callback_query.message, view=view)
    await callback_query.answer('✅ Filtered')


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
    view = UserListView(
        users=users,
        total_balance=total_balance,
        page_size=page_size,
    )
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_users_without_discount_list,
        Text('show-users-without-permanent-discount'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_users_list,
        Text('🙍‍♂ Users'),
        AdminFilter(),
        state='*',
    )
