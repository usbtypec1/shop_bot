from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ChatType

from common.views import edit_message_by_view
from time_sensitive_discounts.callback_data import (
    TimeSensitiveDiscountDetailCallbackData,
)
from time_sensitive_discounts.repositories import (
    TimeSensitiveDiscountRepository,
)
from time_sensitive_discounts.views import TimeSensitiveDiscountDetailView

__all__ = ('register_handlers',)


async def on_show_time_sensitive_discount_detail_menu(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        time_sensitive_discount_repository: TimeSensitiveDiscountRepository,
) -> None:
    await state.finish()
    time_sensitive_discount_id = callback_data['time_sensitive_discount_id']
    time_sensitive_discount_id: int
    time_sensitive_discount = (
        time_sensitive_discount_repository.get_by_id(time_sensitive_discount_id)
    )
    view = TimeSensitiveDiscountDetailView(time_sensitive_discount)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_time_sensitive_discount_detail_menu,
        TimeSensitiveDiscountDetailCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
