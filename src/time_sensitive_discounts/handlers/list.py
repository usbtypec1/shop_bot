from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType, CallbackQuery

from common.filters import AdminFilter
from common.views import answer_view, edit_message_by_view
from time_sensitive_discounts.repositories import (
    TimeSensitiveDiscountRepository,
)
from time_sensitive_discounts.views import TimeSensitiveDiscountListView

__all__ = ('register_handlers',)


async def on_show_time_sensitive_discounts(
        message_or_callback_query: Message | CallbackQuery,
        state: FSMContext,
        time_sensitive_discount_repository: TimeSensitiveDiscountRepository,
) -> None:
    await state.finish()
    time_sensitive_discounts = time_sensitive_discount_repository.get_all()
    view = TimeSensitiveDiscountListView(time_sensitive_discounts)
    if isinstance(message_or_callback_query, Message):
        await answer_view(message=message_or_callback_query, view=view)
    else:
        await edit_message_by_view(
            message=message_or_callback_query.message,
            view=view,
        )


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_time_sensitive_discounts,
        AdminFilter(),
        Text('View Active Discounts'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_show_time_sensitive_discounts,
        AdminFilter(),
        Text('show-time-sensitive-discount-list'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
