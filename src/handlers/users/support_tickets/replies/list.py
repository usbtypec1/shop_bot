from aiogram.types import CallbackQuery

from keyboards.inline.callback_factories import (
    SupportTicketReplyListCallbackData,
)
from loader import dp
from repositories.database import SupportTicketReplyRepository
from database.session import session_factory
from views import SupportTicketReplyView, answer_view


@dp.callback_query_handler(
    SupportTicketReplyListCallbackData().filter(),
    state='*',
)
async def on_show_support_ticket_replies_list(
        callback_query: CallbackQuery,
        callback_data: dict,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    support_ticket_reply_repository = (
        SupportTicketReplyRepository(session_factory)
    )
    support_ticket_replies = (
        support_ticket_reply_repository.get_by_support_ticket_id(
            support_ticket_id=support_ticket_id,
        )
    )
    for support_ticket_reply in support_ticket_replies:
        view = SupportTicketReplyView(support_ticket_reply)
        await answer_view(message=callback_query.message, view=view)
