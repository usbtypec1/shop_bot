from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.filters import AdminFilter
from common.views import edit_message_by_view
from support_tickets.callback_data import AdminSupportTicketDetailCallbackData
from support_tickets.repositories import SupportTicketRepository
from support_tickets.views import AdminSupportTicketDetailView


async def on_show_support_ticket_detail(
        callback_query: CallbackQuery,
        callback_data: dict,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = AdminSupportTicketDetailView(support_ticket)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_support_ticket_detail,
        AdminSupportTicketDetailCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
