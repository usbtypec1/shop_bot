from collections.abc import Iterable

import structlog
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.exceptions import TelegramAPIError
from structlog.stdlib import BoundLogger

__all__ = ('AdminsNotificator',)

logger: BoundLogger = structlog.get_logger('app')


class AdminsNotificator:

    def __init__(
            self,
            *,
            admin_ids: Iterable[int],
            bot: Bot,
    ):
        self.__admin_ids = set(admin_ids)
        self.__bot = bot

    async def notify(
            self,
            text: str,
            reply_markup: InlineKeyboardMarkup | None = None,
    ):
        for admin_id in self.__admin_ids:
            try:
                await self.__bot.send_message(
                    text=text,
                    chat_id=admin_id,
                    reply_markup=reply_markup,
                )
            except TelegramAPIError:
                logger.warning(
                    'Could not send notification to admin',
                    chat_id=admin_id,
                )
