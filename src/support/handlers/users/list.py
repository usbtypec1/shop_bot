from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.views import answer_view
from support.repositories import SupportTicketRepository
from support.views import SupportTicketListView


async def on_show_support_tickets_list(
        message: Message,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    support_tickets = support_ticket_repository.get_by_user_telegram_id(
        user_telegram_id=message.from_user.id,
    )
    view = SupportTicketListView(support_tickets)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_support_tickets_list,
        Text('📓 Tickets'),
        state='*',
    )
