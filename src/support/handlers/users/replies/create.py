from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType

from common.views import answer_view
from support.callback_data import SupportTicketReplyCreateCallbackData
from support.models import SupportTicketReplySource
from support.repositories import (
    SupportTicketReplyRepository,
    SupportTicketRepository
)
from support.states import SupportTicketReplyCreateStates
from support.views import SupportTicketDetailView


async def on_support_ticket_reply_create(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    await SupportTicketReplyCreateStates.text.set()
    await state.update_data(support_ticket_id=support_ticket_id)
    await callback_query.message.edit_text('✏️ Enter Reply')


async def on_support_ticket_reply_input(
        message: Message,
        state: FSMContext,
        support_ticket_repository: SupportTicketRepository,
        support_ticket_reply_repository: SupportTicketReplyRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    support_ticket_id: int = state_data['support_ticket_id']
    support_ticket_reply_repository.create(
        support_ticket_id=support_ticket_id,
        source=SupportTicketReplySource.USER,
        text=message.text,
    )
    support_ticket = support_ticket_repository.get_by_id(support_ticket_id)
    await message.reply('Replied')
    view = SupportTicketDetailView(
        support_ticket=support_ticket,
        has_replies=True,
    )
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_support_ticket_reply_create,
        SupportTicketReplyCreateCallbackData().filter(),
        state='*',
    )
    dispatcher.register_message_handler(
        on_support_ticket_reply_input,
        content_types=ContentType.TEXT,
        state=SupportTicketReplyCreateStates.text,
    )
