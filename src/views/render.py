from aiogram.types import Message

from views.base import View

__all__ = (
    'edit_message_by_view',
    'answer_view',
)


async def edit_message_by_view(
        *,
        message: Message,
        view: View,
) -> Message:
    text = view.get_text()
    reply_markup = view.get_reply_markup()
    return await message.edit_text(text=text, reply_markup=reply_markup)


async def answer_view(
        *,
        message: Message,
        view: View,
) -> Message:
    text = view.get_text()
    reply_markup = view.get_reply_markup()
    return await message.answer(text=text, reply_markup=reply_markup)
