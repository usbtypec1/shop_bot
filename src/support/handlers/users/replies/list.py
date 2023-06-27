from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from common.views import answer_view
from support.callback_data import SupportTicketReplyListCallbackData
from support.repositories import SupportTicketReplyRepository
from support.views import SupportTicketReplyView


async def on_show_support_ticket_replies_list(
        callback_query: CallbackQuery,
        callback_data: dict,
        support_ticket_reply_repository: SupportTicketReplyRepository,
) -> None:
    support_ticket_id: int = callback_data['support_ticket_id']
    support_ticket_replies = (
        support_ticket_reply_repository.get_by_support_ticket_id(
            support_ticket_id=support_ticket_id,
        )
    )
    for support_ticket_reply in support_ticket_replies:
        view = SupportTicketReplyView(support_ticket_reply)
        await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_support_ticket_replies_list,
        SupportTicketReplyListCallbackData().filter(),
        state='*',
    )
