from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from filters.is_admin import IsUserAdmin
from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from services.db_api.session import session_factory
from views import AdminSupportTicketListView, answer_view


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
    view = AdminSupportTicketListView(support_tickets)
    await answer_view(message=message, view=view)
