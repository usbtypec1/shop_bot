from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import SupportTicketDeleteCallbackData
from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from database.session import session_factory
from states.support_states import SupportTicketDeleteStatus
from views import SupportTicketAskDeleteConfirmationView, edit_message_by_view


@dp.callback_query_handler(
    SupportTicketDeleteCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_ask_support_ticket_delete_confirmation(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    await SupportTicketDeleteStatus.confirm.set()
    await state.update_data(support_ticket_id=support_ticket_id)
    view = SupportTicketAskDeleteConfirmationView(support_ticket_id)
    await edit_message_by_view(message=callback_query.message, view=view)


@dp.callback_query_handler(
    IsUserAdmin(),
    Text('support-ticket-delete-confirm'),
    state=SupportTicketDeleteStatus.confirm,
)
async def on_support_ticket_delete_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    support_ticket_id: int = state_data['support_ticket_id']
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_ticket_repository.delete_by_id(support_ticket_id)
    await callback_query.message.edit_text('✅ Deleted')
