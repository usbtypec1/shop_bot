import datetime
from typing import NoReturn

from aiogram import Bot
from aiogram.utils.exceptions import TelegramAPIError

from common.services import get_now_datetime, to_local_time
from common.models import Period
from services.alerts import logger
from support.exceptions import (
    InvalidSupportDateRangeError,
    SupportTicketCreateRateLimitError
)

__all__ = (
    'validate_date_range',
    'check_support_ticket_create_rate_limit',
)

from support.models import SupportTicket
from support.views import SupportTicketStatusChangedNotificationView


def validate_date_range(date_range: str) -> Period:
    try:
        start, end = date_range.split('-')
        start = datetime.datetime.strptime(start, '%m/%d/%Y')
        end = datetime.datetime.strptime(end, '%m/%d/%Y')
    except ValueError:
        raise InvalidSupportDateRangeError
    return Period(start=start, end=end)


def check_support_ticket_create_rate_limit(
        *,
        last_ticket_created_at: datetime.datetime,
) -> None | NoReturn:
    last_ticket_created_at = to_local_time(last_ticket_created_at)
    passed_time = get_now_datetime() - last_ticket_created_at
    remaining_time_in_seconds = 600 - passed_time.total_seconds()
    if remaining_time_in_seconds > 0:
        raise SupportTicketCreateRateLimitError(
            remaining_time_in_seconds=int(remaining_time_in_seconds),
        )


async def notify_user_ticket_status_changed(
        bot: Bot,
        support_ticket: SupportTicket,
) -> None:
    view = SupportTicketStatusChangedNotificationView(support_ticket)
    try:
        await bot.send_message(
            text=view.get_text(),
            chat_id=support_ticket.user_telegram_id,
        )
    except TelegramAPIError:
        logger.warning(
            'User notifications:'
            ' could not send ticket status changed notification',
            user_telegram_id=support_ticket.user_telegram_id,
        )
