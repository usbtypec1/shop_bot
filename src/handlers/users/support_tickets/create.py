from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, Update

import models
from exceptions import SupportTicketCreateRateLimitError
from loader import dp
from repositories.database import ShopInfoRepository
from repositories.database.support_tickets import SupportTicketRepository
from repositories.database.users import UserRepository
from database.session import session_factory
from services.rate_limit import check_support_ticket_create_rate_limit
from states.support_states import SupportTicketCreateStates
from views import answer_view, SupportRulesAcceptView, SupportTicketCreatedView


@dp.errors_handler(
    exception=SupportTicketCreateRateLimitError,
)
async def on_support_ticket_create_rate_limit_error(
        update: Update,
        exception: SupportTicketCreateRateLimitError,
) -> bool:
    await update.message.answer(
        f'You have to wait for {exception.remaining_time_in_seconds}s'
        f' in order to open another ticket'
    )
    return True


@dp.message_handler(
    Text('📋 Submit New Ticket'),
    content_types=ContentType.TEXT,
    state='*',
)
async def on_start_support_ticket_creation_flow(message: Message) -> None:
    support_ticket_repository = SupportTicketRepository(session_factory)
    support_ticket = (
        support_ticket_repository.get_latest_support_ticket_or_none(
            user_telegram_id=message.from_user.id,
        )
    )
    if support_ticket is not None:
        check_support_ticket_create_rate_limit(
            last_ticket_created_at=support_ticket.created_at,
        )

    shop_info_repository = ShopInfoRepository(session_factory)
    rules = shop_info_repository.get_value_or_none(
        key=models.ShopInfo.SUPPORT_RULES.name,
    )
    rules = rules or 'Rules'
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
