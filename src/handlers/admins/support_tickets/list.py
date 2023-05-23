from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from filters.is_admin import IsUserAdmin
from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from database.session import session_factory
from views import (
    answer_view,
    AdminClosedSupportTicketListView,
    AdminOpenSupportTicketListView,
)


@dp.message_handler(
    Text('📗 Open Tickets'),
    IsUserAdmin(),
    state='*',
)
async def on_show_open_tickets_list(
        message: Message,
) -> None:
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_tickets = support_ticket_repository.get_all_open()
    view = AdminOpenSupportTicketListView(support_tickets)
    await answer_view(message=message, view=view)


@dp.message_handler(
    Text('📕 Closed Tickets'),
    IsUserAdmin(),
    state='*',
)
async def on_show_closed_tickets_list(
        message: Message,
) -> None:
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_tickets = support_ticket_repository.get_all_closed()
    view = AdminClosedSupportTicketListView(support_tickets)
    await answer_view(message=message, view=view)
