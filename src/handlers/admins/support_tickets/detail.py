from aiogram.types import CallbackQuery

from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import (
    AdminSupportTicketDetailCallbackData,
)
from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from database.session import session_factory
from views import AdminSupportTicketDetailView, edit_message_by_view


@dp.callback_query_handler(
    AdminSupportTicketDetailCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_show_support_ticket_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = AdminSupportTicketDetailView(support_ticket)
    await edit_message_by_view(message=callback_query.message, view=view)
