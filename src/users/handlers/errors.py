from aiogram import Dispatcher
from aiogram.types import Update

from users.exceptions import UserNotInDatabase

__all__ = ('register_handlers',)


async def user_not_in_db_error(
        update: Update,
        _: UserNotInDatabase,
) -> bool:
    text = "❌ You aren't in the database! Enter /start to register"
    if update.callback_query is not None:
        await update.callback_query.message.answer(text)
    elif update.message is not None:
        await update.message.answer(text)
    return True


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        user_not_in_db_error,
        exception=UserNotInDatabase,
    )
