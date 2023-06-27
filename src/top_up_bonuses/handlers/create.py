from datetime import datetime
from decimal import Decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType, Update, CallbackQuery

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from payments.services import parse_balance_amount
from services.time_utils import get_now_datetime
from time_sensitive_discounts.exceptions import DatetimeValidationError
from time_sensitive_discounts.services import parse_datetime
from top_up_bonuses.exceptions import BonusPercentageValidationError
from top_up_bonuses.repositories import TopUpBonusRepository
from top_up_bonuses.services import parse_top_up_bonus_percentage
from top_up_bonuses.states import TopUpBonusCreateStates
from top_up_bonuses.views import (
    TopUpBonusCreateUpdateAskForConfirmationView,
    TopUpBonusCreateReceiptView,
    TopUpBonusDetailView,
)

__all__ = ('register_handlers',)


async def on_bonus_percentage_validation_error(
        update: Update,
        exception: BonusPercentageValidationError,
) -> bool:
    error_text = str(exception)
    if update.message is not None:
        await update.message.answer(error_text)
    if update.callback_query is not None:
        await update.callback_query.answer(error_text, show_alert=True)
    return True


async def on_start_top_up_bonus_creation_flow(
        message: Message,
) -> None:
    await TopUpBonusCreateStates.minimum_amount.set()
    await message.answer(
        'Enter the minimum amount this bonus will be applied to',
    )


async def on_minimum_top_up_bonus_amount_input(
        message: Message,
        state: FSMContext,
) -> None:
    minimum_top_up_bonus_amount = parse_balance_amount(message.text)
    await TopUpBonusCreateStates.bonus_percentage.set()
    await state.update_data(minimum_amount=minimum_top_up_bonus_amount)
    await message.answer(
        'Enter the amount of % this bonus gives to client'
        ' AFTER topping up their account?'
    )


async def on_top_up_additional_bonus_percentage_input(
        message: Message,
        state: FSMContext,
) -> None:
    bonus_percentage = parse_top_up_bonus_percentage(message.text)
    await TopUpBonusCreateStates.starts_at.set()
    await state.update_data(bonus_percentage=bonus_percentage)
    await message.answer(
        'Enter the time and date this bonus will be STARTED in'
        ' MM/DD/YYYY HH:MM format (Enter any text to Start from now)'
    )


async def on_top_up_bonus_starts_at_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        starts_at = parse_datetime(message.text)
    except DatetimeValidationError:
        starts_at = None
    await TopUpBonusCreateStates.expires_at.set()
    await state.update_data(starts_at=starts_at)
    await message.answer(
        'Enter the time and date this discount will be FINISHED'
        ' in MM/DD/YYYY HH:MM format'
        ' (Enter any text to make if infinite unless deleted by admin later)'
    )


async def on_top_up_bonus_expires_at_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        expires_at = parse_datetime(message.text)
    except DatetimeValidationError:
        expires_at = None
    await TopUpBonusCreateStates.confirm.set()
    await state.update_data(expires_at=expires_at)
    state_data = await state.get_data()
    starts_at: datetime | None = state_data['starts_at']
    bonus_percentage: int = state_data['bonus_percentage']
    minimum_amount: Decimal = state_data['minimum_amount']
    view = TopUpBonusCreateUpdateAskForConfirmationView(
        minimum_amount=minimum_amount,
        bonus_percentage=bonus_percentage,
        starts_at=starts_at,
        expires_at=expires_at,
    )
    await answer_view(message=message, view=view)


async def on_top_up_bonus_creation_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        top_up_bonus_repository: TopUpBonusRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    starts_at: datetime | None = state_data['starts_at']
    expires_at: datetime | None = state_data['expires_at']
    bonus_percentage: int = state_data['bonus_percentage']
    minimum_amount: Decimal = state_data['minimum_amount']
    if starts_at is None:
        starts_at = get_now_datetime()
    top_up_bonus = top_up_bonus_repository.create(
        min_amount_threshold=minimum_amount,
        bonus_percentage=bonus_percentage,
        starts_at=starts_at,
        expires_at=expires_at,
    )
    view = TopUpBonusCreateReceiptView(
        minimum_amount=minimum_amount,
        bonus_percentage=bonus_percentage,
        starts_at=starts_at,
        expires_at=expires_at,
    )
    await edit_message_by_view(message=callback_query.message, view=view)
    view = TopUpBonusDetailView(top_up_bonus)
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_bonus_percentage_validation_error,
        exception=BonusPercentageValidationError,
    )
    dispatcher.register_message_handler(
        on_start_top_up_bonus_creation_flow,
        Text('Create New Top Up Bonus'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_minimum_top_up_bonus_amount_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusCreateStates.minimum_amount,
    )
    dispatcher.register_message_handler(
        on_top_up_additional_bonus_percentage_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusCreateStates.bonus_percentage,
    )
    dispatcher.register_message_handler(
        on_top_up_bonus_starts_at_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusCreateStates.starts_at,
    )
    dispatcher.register_message_handler(
        on_top_up_bonus_expires_at_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusCreateStates.expires_at,
    )
    dispatcher.register_callback_query_handler(
        on_top_up_bonus_creation_confirm,
        AdminFilter(),
        Text('top-up-bonus-create-update-confirm'),
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusCreateStates.confirm,
    )
