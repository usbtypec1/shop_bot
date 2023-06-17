from collections.abc import Iterable
from typing import TypeAlias

import structlog
from aiogram import Bot
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ForceReply,
    ReplyKeyboardRemove,
)
from aiogram.utils.exceptions import TelegramAPIError

__all__ = (
    'View',
    'edit_message_by_view',
    'answer_view',
)

logger = structlog.get_logger('app')

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


async def send_views(
        *,
        bot: Bot,
        chat_ids: Iterable[int],
        view: View,
) -> list[Message]:
    text = view.get_text()
    reply_markup = view.get_reply_markup()
    sent_messages: list[Message] = []
    for chat_id in chat_ids:
        try:
            sent_message = await bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
            )
        except TelegramAPIError:
            logger.error('Could not send view to user', chat_id=chat_id)
        else:
            sent_messages.append(sent_message)
    return sent_messages
