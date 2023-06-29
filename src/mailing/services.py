import asyncio
import contextlib
from collections.abc import Iterable

from aiogram.types import Message
from aiogram.utils.exceptions import TelegramAPIError


async def send_mailing(message: Message, chat_ids: Iterable[int]) -> int:
    received_users_count = 0
    for chat_id in chat_ids:
        with contextlib.suppress(TelegramAPIError):
            await message.copy_to(chat_id=chat_id)
            # Otherwise Telegram will mute bot for some few hours
            await asyncio.sleep(0.05)
            received_users_count += 1
    return received_users_count
