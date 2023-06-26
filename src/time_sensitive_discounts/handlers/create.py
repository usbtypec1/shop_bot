from datetime import datetime

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType, CallbackQuery

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from services.time_utils import get_now_datetime
from time_sensitive_discounts.exceptions import DatetimeValidationError
from time_sensitive_discounts.repositories import (
    TimeSensitiveDiscountRepository,
)
from time_sensitive_discounts.services import parse_datetime
from time_sensitive_discounts.states import TimeSensitiveDiscountCreateStates
from time_sensitive_discounts.views import (
    TimeSensitiveDiscountCreateAskForConfirmationView,
    TimeSensitiveDiscountDetailView,
)
from users.services import parse_permanent_discount

__all__ = ('register_handlers',)


async def on_start_time_sensitive_discount_creation_flow(
        message: Message,
) -> None:
    await TimeSensitiveDiscountCreateStates.starts_at.set()
    await message.answer(
        'Enter the time and date this discount'
        ' will be STARTED in MM/DD/YYYY HH:MM format'
        ' (Enter any text to Start from now)'
    )


async def on_time_sensitive_discount_starts_at_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        starts_at = parse_datetime(message.text)
    except DatetimeValidationError:
        starts_at = get_now_datetime()
    await TimeSensitiveDiscountCreateStates.expires_at.set()
    await state.update_data(starts_at=starts_at)
    await message.answer(
        'Enter the time and date this discount will be FINISHED'
        ' in MM/DD/YYYY HH:MM format'
        ' (Enter any text to make if infinite unless deleted by admin later)'
    )


async def on_time_sensitive_discount_expires_at_input(
        message: Message,
        state: FSMContext,
) -> None:
    try:
        expires_at = parse_datetime(message.text)
    except DatetimeValidationError:
        expires_at = None
    await TimeSensitiveDiscountCreateStates.code.set()
    await state.update_data(expires_at=expires_at)
    await message.answer('What is the code you want to set for discount code?')


async def on_time_sensitive_discount_code_input(
        message: Message,
        state: FSMContext,
) -> None:
    discount_code = message.text
    await TimeSensitiveDiscountCreateStates.discount_value.set()
    await state.update_data(discount_code=discount_code)
    await message.answer(
        'How much discount should be applied with this discount code?'
    )


async def on_time_sensitive_discount_value_input(
        message: Message,
        state: FSMContext,
) -> None:
    discount_value = parse_permanent_discount(message.text)
    await TimeSensitiveDiscountCreateStates.confirm.set()
    await state.update_data(discount_value=discount_value)
    state_data = await state.get_data()
    starts_at: datetime = state_data['starts_at']
    expires_at: datetime = state_data['expires_at']
    view = TimeSensitiveDiscountCreateAskForConfirmationView(
        starts_at=starts_at,
        expires_at=expires_at,
    )
    await answer_view(message=message, view=view)


async def on_time_sensitive_discount_code_creation_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        time_sensitive_discount_repository: TimeSensitiveDiscountRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    starts_at: datetime | None = state_data['starts_at']
    expires_at: datetime | None = state_data['expires_at']
    code: str = state_data['discount_code']
    value: int = state_data['discount_value']
    time_sensitive_discount = time_sensitive_discount_repository.create(
        starts_at=starts_at,
        expires_at=expires_at,
        code=code,
        value=value,
    )
    view = TimeSensitiveDiscountDetailView(time_sensitive_discount)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_start_time_sensitive_discount_creation_flow,
        AdminFilter(),
        Text('Create New Discount'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_time_sensitive_discount_starts_at_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TimeSensitiveDiscountCreateStates.starts_at,
    )
    dispatcher.register_message_handler(
        on_time_sensitive_discount_expires_at_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TimeSensitiveDiscountCreateStates.expires_at,
    )
    dispatcher.register_message_handler(
        on_time_sensitive_discount_code_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TimeSensitiveDiscountCreateStates.code,
    )
    dispatcher.register_message_handler(
        on_time_sensitive_discount_value_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state=TimeSensitiveDiscountCreateStates.discount_value,
    )
    dispatcher.register_callback_query_handler(
        on_time_sensitive_discount_code_creation_confirm,
        AdminFilter(),
        Text('time-sensitive-discount-create-confirm'),
        chat_type=ChatType.PRIVATE,
        state=TimeSensitiveDiscountCreateStates.confirm,
    )
