from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ChatType

from common.filters import AdminFilter
from common.views import edit_message_by_view
from time_sensitive_discounts.callback_data import (
    TimeSensitiveDiscountDeleteCallbackData,
)
from time_sensitive_discounts.repositories import (
    TimeSensitiveDiscountRepository,
)
from time_sensitive_discounts.states import TimeSensitiveDiscountDeleteStates
from time_sensitive_discounts.views import (
    TimeSensitiveDiscountDeleteAskForConfirmationView,
    TimeSensitiveDiscountListView,
)

__all__ = ('register_handlers',)


async def on_ask_delete_time_sensitive_discount_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    time_sensitive_discount_id = callback_data['time_sensitive_discount_id']
    time_sensitive_discount_id: int
    view = TimeSensitiveDiscountDeleteAskForConfirmationView(
        time_sensitive_discount_id=time_sensitive_discount_id,
    )
    await TimeSensitiveDiscountDeleteStates.confirm.set()
    await state.update_data(
        time_sensitive_discount_id=time_sensitive_discount_id,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_delete_time_sensitive_discount_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        time_sensitive_discount_repository: TimeSensitiveDiscountRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    time_sensitive_discount_id: int = state_data['time_sensitive_discount_id']
    time_sensitive_discount_repository.delete_by_id(
        time_sensitive_discount_id=time_sensitive_discount_id,
    )
    time_sensitive_discounts = time_sensitive_discount_repository.get_all()
    view = TimeSensitiveDiscountListView(time_sensitive_discounts)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_ask_delete_time_sensitive_discount_confirmation,
        AdminFilter(),
        TimeSensitiveDiscountDeleteCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_delete_time_sensitive_discount_confirm,
        AdminFilter(),
        Text('time-sensitive-discount-delete-confirm'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
