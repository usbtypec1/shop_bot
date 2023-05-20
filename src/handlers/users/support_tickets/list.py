from aiogram.dispatcher.filters import Text
from aiogram.types import Message

from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from repositories.database.users import UserRepository
from services.db_api.session import session_factory
from views import SupportTicketListView, answer_view


@dp.message_handler(
    Text('📓 Tickets'),
    state='*',
)
async def on_show_support_tickets_list(message: Message) -> None:
    user_repository = UserRepository(session_factory)
    support_ticket_repository = SupportTicketRepository(session_factory)
    user = user_repository.get_by_telegram_id(message.from_user.id)
    support_tickets = support_ticket_repository.get_by_user_id(user.id)
    view = SupportTicketListView(support_tickets)
    await answer_view(message=message, view=view)
