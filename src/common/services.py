from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal
from typing import NewType
from zoneinfo import ZoneInfo

import structlog
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.exceptions import TelegramAPIError
from structlog.stdlib import BoundLogger

__all__ = (
    'AdminsNotificator',
    'get_now_datetime',
    'to_local_time',
    'render_money',
)

logger: BoundLogger = structlog.get_logger('app')

TIMEZONE = ZoneInfo('US/Eastern')
UTC = ZoneInfo('UTC')
TZAware = NewType('TZAware', datetime)


def get_now_datetime() -> TZAware:
    return TZAware(datetime.now(tz=TIMEZONE))


def to_local_time(dt: datetime) -> TZAware:
    return TZAware(dt.replace(tzinfo=UTC).astimezone(TIMEZONE))


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


def render_money(amount: Decimal) -> str:
    amount = f'{amount:f}'

    if amount.count('.') == 1:
        integer_part, decimal_part = str(amount).split('.')
        trimmed_decimal_part = decimal_part.rstrip('0')
        return f'{integer_part}.{trimmed_decimal_part}'.rstrip('.')

    return amount
