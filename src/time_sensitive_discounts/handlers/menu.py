from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ChatType

from common.filters import AdminFilter
from common.views import answer_view
from time_sensitive_discounts.views import TimeSensitiveDiscountMenuView

__all__ = ('register_handlers',)


async def on_show_time_sensitive_discount_menu(
        message: Message,
        state: FSMContext,
) -> None:
    await state.finish()
    view = TimeSensitiveDiscountMenuView()
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_time_sensitive_discount_menu,
        AdminFilter(),
        Text('% Time Sensitive Discounts'),
        content_types=ContentType.TEXT,
        chat_type=ChatType.PRIVATE,
        state='*',
    )
