import structlog
from aiogram.utils.exceptions import TelegramAPIError

import models
from loader import bot
from views import SupportTicketStatusChangedNotificationView

logger = structlog.get_logger('app')

__all__ = ('notify_user_ticket_status_changed',)


async def notify_user_ticket_status_changed(
        support_ticket: models.SupportTicket,
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
