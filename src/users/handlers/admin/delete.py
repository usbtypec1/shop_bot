from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ChatType

from common.filters import AdminFilter
from common.views import edit_message_by_view, answer_view
from users.callback_data import UserDeleteCallbackData

__all__ = ('register_handlers',)

from users.repositories import UserRepository
from users.services import calculate_total_balance

from users.states import UserDeleteStates
from users.views import (
    UserDeleteAskForConfirmationView, UserDeleteSuccessView,
    UserListView
)


async def on_ask_user_delete_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        user_repository: UserRepository,
) -> None:
    user_id: int = callback_data['user_id']
    user = user_repository.get_by_id(user_id)
    await UserDeleteStates.confirm.set()
    await state.update_data(user_id=user_id)
    view = UserDeleteAskForConfirmationView(user)
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_user_delete_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
) -> None:
    state_data = await state.get_data()
    user_id: int = state_data['user_id']
    deleted_user = user_repository.get_by_id(user_id)
    user_repository.delete_by_id(user_id)
    users = user_repository.get_by_usernames_and_ids(limit=10, offset=0)
    total_balance = calculate_total_balance(users)
    view = UserDeleteSuccessView(deleted_user)
    await edit_message_by_view(message=callback_query.message, view=view)
    view = UserListView(users=users, total_balance=total_balance)
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_ask_user_delete_confirmation,
        AdminFilter(),
        UserDeleteCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_user_delete_confirm,
        AdminFilter(),
        chat_type=ChatType.PRIVATE,
        state=UserDeleteStates.confirm,
    )
