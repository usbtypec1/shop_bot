from aiogram.types import CallbackQuery

import models
from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import (
    SupportTicketStatusListCallbackData,
    SupportTicketStatusUpdateCallbackData,
)
from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from services.alerts import notify_user_ticket_status_changed
from services.db_api.session import session_factory
from views import (
    SupportTicketStatusListView,
    edit_message_by_view,
    AdminSupportTicketDetailView,
)


@dp.callback_query_handler(
    SupportTicketStatusUpdateCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_support_ticket_status_update(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    status: models.SupportTicketStatus = callback_data['status']
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_ticket_repository.update_support_ticket_status(
        support_ticket_id=support_ticket_id,
        status=status,
    )
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = AdminSupportTicketDetailView(support_ticket)
    await edit_message_by_view(message=callback_query.message, view=view)
    await notify_user_ticket_status_changed(support_ticket)


@dp.callback_query_handler(
    SupportTicketStatusListCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_show_support_ticket_status_list(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = SupportTicketStatusListView(
        support_ticket_id=support_ticket_id,
        current_status=support_ticket.status,
    )
    await edit_message_by_view(message=callback_query.message, view=view)
