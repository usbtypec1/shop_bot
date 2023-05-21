from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, ReplyKeyboardRemove

from loader import dp
from repositories.database.support_tickets import SupportTicketRepository
from repositories.database.users import UserRepository
from services.db_api.queries import get_rules
from services.db_api.session import session_factory
from states.support_states import SupportTicketCreateStates
from views import answer_view, SupportRulesAcceptView, SupportTicketCreatedView


@dp.message_handler(
    Text('📋 Submit New Ticket'),
    content_types=ContentType.TEXT,
    state='*',
)
async def on_start_support_ticket_creation_flow(message: Message) -> None:
    with session_factory() as session:
        rules = get_rules(session)
    rules = rules.value if rules is not None else 'Rules'
    await SupportTicketCreateStates.confirm_rules.set()
    view = SupportRulesAcceptView()
    await message.answer(rules)
    await answer_view(message=message, view=view)


@dp.message_handler(
    Text('✅ I Did'),
    content_types=ContentType.TEXT,
    state=SupportTicketCreateStates.confirm_rules,
)
async def on_accept_support_rules(message: Message) -> None:
    await SupportTicketCreateStates.subject.set()
    await message.answer(
        'Enter The Subject of your inquiry'
        ' (Please make it short and without any symbols)',
    )


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=SupportTicketCreateStates.subject,
)
async def on_support_ticket_subject_input(
        message: Message,
        state: FSMContext,
) -> None:
    await state.update_data(subject=message.text)
    await SupportTicketCreateStates.issue.set()
    await message.answer(
        'Enter your message (Please provide as much information'
        ' as possible like Order Number, Payment details)'
    )


@dp.message_handler(
    content_types=ContentType.TEXT,
    state=SupportTicketCreateStates.issue,
)
async def on_support_ticket_issue_input(
        message: Message,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    subject = state_data['subject']
    issue = message.text

    user_repository = UserRepository(session_factory)
    support_ticket_repository = SupportTicketRepository(session_factory)

    user = user_repository.get_by_telegram_id(message.from_user.id)
    support_ticket = support_ticket_repository.create(
        user_id=user.id,
        user_telegram_id=message.from_user.id,
        subject=subject,
        issue=issue,
    )

    view = SupportTicketCreatedView(support_ticket.id)
    await answer_view(message=message, view=view)
