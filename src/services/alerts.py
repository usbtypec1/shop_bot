import structlog
from aiogram import Bot
from aiogram.utils.exceptions import TelegramAPIError

from support_tickets.models import SupportTicket
from support_tickets.views import SupportTicketStatusChangedNotificationView

logger = structlog.get_logger('app')

__all__ = ('notify_user_ticket_status_changed',)


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
