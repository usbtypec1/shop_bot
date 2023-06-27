from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.views import edit_message_by_view
from support.callback_data import SupportTicketDetailCallbackData
from support.repositories import (
    SupportTicketRepository,
    SupportTicketReplyRepository,
)
from support.views import SupportTicketDetailView


async def on_show_support_ticket_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        support_ticket_repository: SupportTicketRepository,
        support_ticket_reply_repository: SupportTicketReplyRepository,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    support_ticket_replies = (
        support_ticket_reply_repository.get_by_support_ticket_id(
            support_ticket_id=support_ticket.id,
        )
    )
    view = SupportTicketDetailView(
        support_ticket=support_ticket,
        has_replies=bool(support_ticket_replies),
    )
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_support_ticket_detail,
        SupportTicketDetailCallbackData().filter(),
        state='*',
    )
