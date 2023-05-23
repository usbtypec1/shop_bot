import aiogram.types

import responses.profile
from loader import dp
from aiogram import filters

from services import db_api
from services.db_api import queries
import exceptions


# @dp.message_handler(filters.Text('📱 Profile'))
# async def profile(message: aiogram.types.Message):
#     with db_api.create_session() as session:
#         user = queries.get_user(session, telegram_id=message.from_user.id)
#         if user is None:
#             raise exceptions.UserNotInDatabase
#         queries.get_purchases(session, message.from_user.id)
#         await responses.profile.ProfileResponse(
#             message, user.telegram_id, user.username,
#             queries.count_user_purchases(session, user.id),
#             queries.get_user_orders_amount(session, user.id),
#             queries.get_purchases(session, user.id, limit=10)
#         )

@dp.message_handler(filters.Text('📱 Profile'))
async def profile(message: aiogram.types.Message):
    with db_api.create_session() as session:
        user = queries.get_user(session, telegram_id=message.from_user.id)
        if user is None:
            raise exceptions.UserNotInDatabase
        user_balance = queries.get_user_balance(session, user.id)  # liked to a new query get_user_balance()
        await responses.profile.ProfileResponse(
            message, user.telegram_id, user.username, user_balance,
            queries.count_user_purchases(session, user.id),
            queries.get_user_orders_amount(session, user.id),
            queries.get_purchases(session, user.id, limit=10)
        )
