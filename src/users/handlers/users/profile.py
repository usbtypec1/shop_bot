from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

import database
import responses.profile
from database import queries
from users.exceptions import UserNotInDatabase


async def profile(message: Message) -> None:
    with database.create_session() as session:
        user = queries.get_user(session, telegram_id=message.from_user.id)
        if user is None:
            raise UserNotInDatabase
        user_balance = queries.get_user_balance(session, user.id)
        await responses.profile.ProfileResponse(
            message, user.telegram_id, user.username, user_balance,
            queries.count_user_purchases(session, user.id),
            queries.get_user_orders_amount(session, user.id),
            queries.get_purchases(session, user.id, limit=10)
        )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        Text('📱 Profile'),
        state='*',
    )
