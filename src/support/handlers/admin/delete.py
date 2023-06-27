from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from common.filters import AdminFilter
from common.views import edit_message_by_view
from support.callback_data import SupportTicketDeleteCallbackData
from support.repositories import SupportTicketRepository
from support.states import SupportTicketDeleteStatus
from support.views import SupportTicketAskDeleteConfirmationView


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


async def on_support_ticket_delete_confirm(
        callback_query: CallbackQuery,
        state: FSMContext,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    state_data = await state.get_data()
    support_ticket_id: int = state_data['support_ticket_id']
    support_ticket_repository.delete_by_id(support_ticket_id)
    await callback_query.message.edit_text('✅ Deleted')


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_ask_support_ticket_delete_confirmation,
        SupportTicketDeleteCallbackData().filter(),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_support_ticket_delete_confirm,
        AdminFilter(),
        Text('support-ticket-delete-confirm'),
        state=SupportTicketDeleteStatus.confirm,
    )
