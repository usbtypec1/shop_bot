from datetime import datetime
from decimal import Decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType, CallbackQuery

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from payments.services import parse_balance_amount
from services.time_utils import get_now_datetime
from time_sensitive_discounts.exceptions import DatetimeValidationError
from time_sensitive_discounts.services import parse_datetime
from top_up_bonuses.callback_data import TopUpBonusUpdateCallbackData
from top_up_bonuses.repositories import TopUpBonusRepository
from top_up_bonuses.services import parse_top_up_bonus_percentage
from top_up_bonuses.states import TopUpBonusUpdateStates
from top_up_bonuses.views import (
    TopUpBonusCreateUpdateAskForConfirmationView,
    TopUpBonusDetailView,
    TopUpBonusUpdateReceiptView,
)

__all__ = ('register_handlers',)


async def on_start_top_up_bonus_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    top_up_bonus_id: int = callback_data['top_up_bonus_id']
    await TopUpBonusUpdateStates.minimum_amount.set()
    await state.update_data(top_up_bonus_id=top_up_bonus_id)
    await callback_query.message.edit_text(
        'Enter the new amount of top up this bonus will be applied to?'
    )


async def on_minimum_top_up_bonus_amount_input(
        message: Message,
        state: FSMContext,
) -> None:
    minimum_top_up_bonus_amount = parse_balance_amount(message.text)
    await TopUpBonusUpdateStates.bonus_percentage.set()
    await state.update_data(minimum_amount=minimum_top_up_bonus_amount)
    await message.answer(
        'Enter the new amount of top up bonus that will be applied?'
    )


async def on_top_up_additional_bonus_percentage_input(
        message: Message,
        state: FSMContext,
) -> None:
    bonus_percentage = parse_top_up_bonus_percentage(message.text)
    await TopUpBonusUpdateStates.starts_at.set()
    await state.update_data(bonus_percentage=bonus_percentage)
    await message.answer(
        'Enter the new time and date this bonus will be STARTED in MM-DD-YYYY'
        ' HH:MM format (Enter any text to Start from now)'
    )


async def on_top_up_bonus_starts_at_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        starts_at = parse_datetime(message.text)
    except DatetimeValidationError:
        starts_at = None
    await TopUpBonusUpdateStates.expires_at.set()
    await state.update_data(starts_at=starts_at)
    await message.answer(
        'Enter the new time and date this discount will be FINISHED in'
        ' MM-DD-YYYY HH:MM format'
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
    await TopUpBonusUpdateStates.confirm.set()
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
    top_up_bonus_id: int = state_data['top_up_bonus_id']
    starts_at: datetime | None = state_data['starts_at']
    expires_at: datetime | None = state_data['expires_at']
    bonus_percentage: int = state_data['bonus_percentage']
    minimum_amount: Decimal = state_data['minimum_amount']

    old_top_up_bonus = top_up_bonus_repository.get_by_id(top_up_bonus_id)
    view = TopUpBonusUpdateReceiptView(
        old_minimum_amount=old_top_up_bonus.min_amount_threshold,
        old_bonus_percentage=old_top_up_bonus.bonus_percentage,
        new_minimum_amount=minimum_amount,
        new_bonus_percentage=bonus_percentage,
        new_starts_at=starts_at,
        new_expires_at=expires_at,
    )

    if starts_at is None:
        starts_at = get_now_datetime()

    top_up_bonus = top_up_bonus_repository.update(
        id_=top_up_bonus_id,
        min_amount_threshold=minimum_amount,
        bonus_percentage=bonus_percentage,
        starts_at=starts_at,
        expires_at=expires_at,
    )
    await edit_message_by_view(message=callback_query.message, view=view)
    view = TopUpBonusDetailView(top_up_bonus)
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_top_up_bonus_update_flow,
        TopUpBonusUpdateCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_minimum_top_up_bonus_amount_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusUpdateStates.minimum_amount,
    )
    dispatcher.register_message_handler(
        on_top_up_additional_bonus_percentage_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusUpdateStates.bonus_percentage,
    )
    dispatcher.register_message_handler(
        on_top_up_bonus_starts_at_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusUpdateStates.starts_at,
    )
    dispatcher.register_message_handler(
        on_top_up_bonus_expires_at_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusUpdateStates.expires_at,
    )
    dispatcher.register_callback_query_handler(
        on_top_up_bonus_creation_confirm,
        AdminFilter(),
        Text('top-up-bonus-create-update-confirm'),
        chat_type=ChatType.PRIVATE,
        state=TopUpBonusUpdateStates.confirm,
    )
