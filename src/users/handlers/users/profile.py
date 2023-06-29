from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.views import answer_view
from sales.repositories import SaleRepository
from users.repositories import UserRepository
from users.views import UserProfileView

__all__ = ('on_show_profile_menu',)


async def on_show_profile_menu(
        message: Message,
        user_repository: UserRepository,
        sale_repository: SaleRepository
) -> None:
    user = user_repository.get_by_telegram_id(message.from_user.id)
    total_orders_count = sale_repository.count_by_user_id(user.id)
    total_orders_cost = sale_repository.calculate_total_cost_by_user_id(user.id)
    view = UserProfileView(
        user=user,
        total_orders_cost=total_orders_cost,
        total_orders_count=total_orders_count,
    )
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        Text('📱 Profile'),
        state='*',
    )
