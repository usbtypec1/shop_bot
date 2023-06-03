import aiogram
from aiogram import filters

import responses.statistics
from common import models
from filters import is_admin
from loader import dp
import database
from database import queries, session_factory
from repositories.database.users import UserRepository


@dp.message_handler(filters.Text('📊 Statistics'), is_admin.IsUserAdmin())
async def statistics(message: aiogram.types.Message):
    await responses.statistics.StatisticsMenuResponse(message)


@dp.message_handler(filters.Text('📊 General'), is_admin.IsUserAdmin())
async def general_statistics(message: aiogram.types.Message):
    user_repository = UserRepository(session_factory)
    with database.create_session() as session:
        buyers = []
        for telegram_id, username, quantity, amount in queries.get_buyers(session):
            buyer: models.Buyer = {
                'telegram_id': telegram_id, 'username': username,
                'purchase_number': quantity, 'orders_amount': amount
            }
            buyers.append(buyer)

        await responses.statistics.StatisticsResponse(
            message,
            user_repository.get_total_count(),
            queries.get_total_orders_amount(session),
            queries.count_purchases(session),
            queries.get_purchases(session),
            buyers
        )


@dp.message_handler(filters.Text('📆 Daily'), is_admin.IsUserAdmin())
async def daily_statistics(message: aiogram.types.Message):
    await message.answer('🚧 Under Development')
