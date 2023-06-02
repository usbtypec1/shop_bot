from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType

from filters.is_admin import IsUserAdmin
from keyboards.inline.callback_factories import (
    SupportTicketAnswerUpdateCallbackData,
)
from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from database.session import session_factory
from states.support_states import AdminSupportTicketUpdateStates
from views import AdminSupportTicketDetailView, answer_view


@dp.callback_query_handler(
    SupportTicketAnswerUpdateCallbackData().filter(),
    IsUserAdmin(),
    state='*',
)
async def on_start_support_ticket_answer_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    await AdminSupportTicketUpdateStates.answer.set()
    await state.update_data(support_ticket_id=support_ticket_id)
    await callback_query.message.edit_text('✏️ Enter Answer')


@dp.message_handler(
    IsUserAdmin(),
    content_types=ContentType.TEXT,
    state=AdminSupportTicketUpdateStates.answer,
)
async def on_support_ticket_answer_input(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    support_ticket_id: int = state_data['support_ticket_id']
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_ticket_repository.update_support_ticket_answer(
        support_ticket_id=support_ticket_id,
        answer=message.text,
    )
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = AdminSupportTicketDetailView(support_ticket)
    await answer_view(message=message, view=view)
