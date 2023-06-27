from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType

from common.filters import AdminFilter
from common.views import answer_view
from support.callback_data import SupportTicketAnswerUpdateCallbackData
from support.repositories import SupportTicketRepository
from support.states import AdminSupportTicketUpdateStates
from support.views import AdminSupportTicketDetailView


async def on_start_support_ticket_answer_update_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    await AdminSupportTicketUpdateStates.answer.set()
    await state.update_data(support_ticket_id=support_ticket_id)
    await callback_query.message.edit_text('✏️ Enter Answer')


async def on_support_ticket_answer_input(
        message: Message,
        state: FSMContext,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    support_ticket_id: int = state_data['support_ticket_id']
    support_ticket_repository.update_support_ticket_answer(
        support_ticket_id=support_ticket_id,
        answer=message.text,
    )
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    view = AdminSupportTicketDetailView(support_ticket)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_start_support_ticket_answer_update_flow,
        SupportTicketAnswerUpdateCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_support_ticket_answer_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=AdminSupportTicketUpdateStates.answer,
    )
