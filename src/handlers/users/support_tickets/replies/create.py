from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ContentType

import models
from keyboards.inline.callback_factories import (
    SupportTicketReplyCreateCallbackData,
)
from loader import dp
from repositories.database import SupportTicketReplyRepository
from services.db_api.session import session_factory
from states.support_states import SupportTicketReplyCreateStates


@dp.callback_query_handler(
    SupportTicketReplyCreateCallbackData().filter(),
    state='*',
)
async def on_support_ticket_reply_create(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    await SupportTicketReplyCreateStates.text.set()
    await state.update_data(support_ticket_id=support_ticket_id)
    await callback_query.message.edit_text('✏️ Enter Reply')


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=SupportTicketReplyCreateStates.text,
)
async def on_support_ticket_reply_input(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    support_ticket_id: int = state_data['support_ticket_id']
    support_ticket_reply_repository = SupportTicketReplyRepository(
        session_factory=session_factory,
    )
    support_ticket_reply_repository.create(
        support_ticket_id=support_ticket_id,
        source=models.SupportTicketReplySource.USER,
        text=message.text,
    )
    await message.answer('Replied')
