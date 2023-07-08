from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

import database
from common.filters import AdminFilter
from common.models import Buyer
from common.views import answer_view
from sales.repositories import SaleRepository
from users.repositories import UserRepository
from users.views import UserStatisticsMenuView, UserGeneralStatisticsView


async def on_show_user_statistics_menu(message: Message) -> None:
    await answer_view(message=message, view=UserStatisticsMenuView())


async def on_show_user_general_statistics(
        message: Message,
        sale_repository: SaleRepository,
        user_repository: UserRepository,
) -> None:
    buyers_count = user_repository.get_total_count()
    total_orders_count = sale_repository.count_all()
    total_orders_cost = sale_repository.calculate_total_cost()

    with database.create_session() as session:
        products_sold_units_quantity = queries.get_purchases(session)
        buyers: list[Buyer] = [
            {
                'telegram_id': telegram_id,
                'username': username,
                'purchase_number': quantity,
                'orders_amount': amount,
            }
            for telegram_id, username, quantity, amount
            in queries.get_buyers(session)
        ]

    view = UserGeneralStatisticsView(
        buyers_count=buyers_count,
        orders_total_cost=total_orders_cost,
        sold_products_count=total_orders_count,
        sold_product_units_quantity=products_sold_units_quantity,
        active_buyers=buyers,
    )
    await answer_view(message=message, view=view)


async def on_show_user_daily_statistics(message: Message) -> None:
    await message.answer('🚧 Under Development')


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_user_statistics_menu,
        Text('📊 Statistics'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_user_general_statistics,
        Text('📊 General'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_user_daily_statistics,
        Text('📆 Daily'),
        AdminFilter(),
        state='*',
    )
