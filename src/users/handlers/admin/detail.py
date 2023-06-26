from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.filters import AdminFilter
from common.views import edit_message_by_view
from sales.repositories import SaleRepository
from users.callback_data import UserDetailCallbackData
from users.repositories import UserRepository
from users.views import UserDetailView

__all__ = ('register_handlers',)


async def on_show_user_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        user_repository: UserRepository,
        sale_repository: SaleRepository,
) -> None:
    user_id: int = callback_data['user_id']
    user = user_repository.get_by_id(user_id)
    orders_count = sale_repository.count_by_user_id(user_id)
    view = UserDetailView(
        user=user,
        number_of_orders=orders_count,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_user_detail,
        AdminFilter(),
        UserDetailCallbackData().filter(),
        state='*',
    )
