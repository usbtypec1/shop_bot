from typing import TypeAlias

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ForceReply,
    ReplyKeyboardRemove,
)

__all__ = (
    'View',
    'edit_message_by_view',
    'answer_view',
)

ReplyMarkup: TypeAlias = (
        InlineKeyboardMarkup
        | ReplyKeyboardMarkup
        | ForceReply
        | ReplyKeyboardRemove
)


class View:
    text: str | None = None
    reply_markup: ReplyMarkup | None = None

    def get_text(self) -> str | None:
        return self.text

    def get_reply_markup(self) -> ReplyMarkup | None:
        return self.reply_markup


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
