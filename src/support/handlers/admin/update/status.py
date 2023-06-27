from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.filters import AdminFilter
from common.views import edit_message_by_view
from services.alerts import notify_user_ticket_status_changed
from support.callback_data import (
    SupportTicketStatusUpdateCallbackData,
    SupportTicketStatusListCallbackData,
)
from support.models import SupportTicketStatus
from support.repositories import SupportTicketRepository
from support.views import (
    SupportTicketStatusListView,
    AdminSupportTicketDetailView,
)


async def on_support_ticket_status_update(
        callback_query: CallbackQuery,
        callback_data: dict,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    status: SupportTicketStatus = callback_data['status']
    support_ticket_repository.update_support_ticket_status(
        support_ticket_id=support_ticket_id,
        status=status,
    )
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = AdminSupportTicketDetailView(support_ticket)
    await edit_message_by_view(message=callback_query.message, view=view)
    await notify_user_ticket_status_changed(support_ticket)


async def on_show_support_ticket_status_list(
        callback_query: CallbackQuery,
        callback_data: dict,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = SupportTicketStatusListView(
        support_ticket_id=support_ticket_id,
        current_status=support_ticket.status,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_support_ticket_status_update,
        SupportTicketStatusUpdateCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_show_support_ticket_status_list,
        SupportTicketStatusListCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
