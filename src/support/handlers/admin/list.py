from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from common.filters import AdminFilter
from common.views import answer_view
from support.repositories import SupportTicketRepository
from support.views import (
    AdminOpenSupportTicketListView,
    AdminClosedSupportTicketListView,
)


async def on_show_open_tickets_list(
        message: Message,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    support_tickets = support_ticket_repository.get_all_open()
    view = AdminOpenSupportTicketListView(support_tickets)
    await answer_view(message=message, view=view)


async def on_show_closed_tickets_list(
        message: Message,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    support_tickets = support_ticket_repository.get_all_closed()
    view = AdminClosedSupportTicketListView(support_tickets)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_open_tickets_list,
        Text('📗 Open Tickets'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_show_closed_tickets_list,
        Text('📕 Closed Tickets'),
        AdminFilter(),
        state='*',
    )
