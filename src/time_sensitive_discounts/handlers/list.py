from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType

from common.filters import AdminFilter
from common.views import answer_view
from time_sensitive_discounts.repositories import (
    TimeSensitiveDiscountRepository,
)
from time_sensitive_discounts.views import TimeSensitiveDiscountListView

__all__ = ('register_handlers',)


async def on_show_active_time_sensitive_discounts(
        message: Message,
        state: FSMContext,
        time_sensitive_discount_repository: TimeSensitiveDiscountRepository,
) -> None:
    await state.finish()
    time_sensitive_discounts = time_sensitive_discount_repository.get_all()
    view = TimeSensitiveDiscountListView(time_sensitive_discounts)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_active_time_sensitive_discounts,
        AdminFilter(),
        Text('View Active Discounts'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
