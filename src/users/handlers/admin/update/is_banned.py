from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from common.filters import AdminFilter
from common.views import edit_message_by_view
from sales.repositories import SaleRepository
from users.callback_data import UserUpdateCallbackData
from users.repositories import UserRepository
from users.views import UserBannedStatusToggleView, UserDetailView

__all__ = ('register_handlers',)


async def on_banned_status_toggle(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        user_repository: UserRepository,
) -> None:
    user_id: int = callback_data['user_id']
    user = user_repository.get_by_id(user_id)
    await state.update_data(
        user_id=user_id,
        user_telegram_id=user.telegram_id,
    )
    view = UserBannedStatusToggleView(user)
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_banned_status_toggle_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_repository: UserRepository,
        sale_repository: SaleRepository,
) -> None:
    state_data = await state.get_data()
    user_id: int = state_data['user_id']
    user_telegram_id: int = state_data['user_telegram_id']
    is_banned = user_repository.is_banned(user_telegram_id)

    if is_banned:
        user_repository.unban_by_id(user_id)
    else:
        user_repository.ban_by_id(user_id)

    user = user_repository.get_by_id(user_id)
    orders_count = sale_repository.count_by_user_id(user_id)
    view = UserDetailView(user=user, number_of_orders=orders_count)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_banned_status_toggle,
        AdminFilter(),
        UserUpdateCallbackData().filter(field='banned-status'),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_banned_status_toggle_confirm,
        AdminFilter(),
        Text('banned-status-toggle-confirm'),
        state='*',
    )
