from aiogram import Dispatcher
from aiogram.types import Update

from users.exceptions import (
    UserNotInDatabase,
    PermanentDiscountValidationError,
    InsufficientUserBalanceError,
)

__all__ = ('register_handlers',)


async def on_insufficient_user_balance_error(
        update: Update,
        exception: InsufficientUserBalanceError,
) -> bool:
    text = str(exception)
    if update.callback_query is not None:
        await update.callback_query.message.answer(text)
    elif update.message is not None:
        await update.message.answer(text)
    return True


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


async def on_permanent_discount_validation_error(
        update: Update,
        _: PermanentDiscountValidationError,
) -> bool:
    text = '❌ Discount value must be within the range of 0 to 99'
    if update.message is not None:
        await update.message.answer(text)
    if update.callback_query is not None:
        await update.callback_query.answer(text, show_alert=True)
    return True


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_insufficient_user_balance_error,
        exception=InsufficientUserBalanceError,
    )
    dispatcher.register_errors_handler(
        user_not_in_db_error,
        exception=UserNotInDatabase,
    )
    dispatcher.register_errors_handler(
        on_permanent_discount_validation_error,
        exception=PermanentDiscountValidationError,
    )
