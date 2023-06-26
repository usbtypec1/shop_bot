from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, Message, ChatType, ContentType

from common.filters import AdminFilter
from common.views import answer_view
from users.repositories import UserRepository
from users.services import (
    parse_users_identifiers_for_search,
    calculate_total_balance,
)
from users.states import SearchUsersStates
from users.views import UserListView

__all__ = ('register_handlers',)


async def on_start_search_users_flow(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    await state.finish()
    await callback_query.message.answer('🆔 Enter usernames or ids')
    await SearchUsersStates.waiting_identifiers.set()


async def on_users_identifiers_for_search_input(
        message: Message,
        state: FSMContext,
        user_repository: UserRepository,
):
    await state.finish()
    page, page_size = 0, 10
    users_identifiers = parse_users_identifiers_for_search(message.text)
    users = user_repository.get_by_usernames_and_ids(
        usernames=users_identifiers.usernames,
        user_ids=users_identifiers.user_ids,
        limit=page_size,
        offset=page * page_size,
    )
    total_balance = calculate_total_balance(users)
    sent_message = await message.answer(
        f'🔡 Found users with these usernames and ids: {message.text}'
    )
    view = UserListView(
        users=users,
        total_balance=total_balance,
        users_filter=sent_message.message_id,
        page=page,
        page_size=page_size,
    )
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_search_users_flow,
        AdminFilter(),
        Text('search-users'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_users_identifiers_for_search_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=SearchUsersStates.waiting_identifiers,
    )
