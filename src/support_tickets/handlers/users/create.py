from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ContentType, Update

from common.views import answer_view
from services.rate_limit import check_support_ticket_create_rate_limit
from shop_info.models import ShopInfo
from shop_info.repositories import ShopInfoRepository
from support_tickets.exceptions import SupportTicketCreateRateLimitError
from support_tickets.repositories import SupportTicketRepository
from support_tickets.states import SupportTicketCreateStates
from support_tickets.views import (
    SupportRulesAcceptView,
    SupportTicketCreatedView,
)
from users.repositories import UserRepository


async def on_support_ticket_create_rate_limit_error(
        update: Update,
        exception: SupportTicketCreateRateLimitError,
) -> bool:
    await update.message.answer(
        f'You have to wait for {exception.remaining_time_in_seconds}s'
        f' in order to open another ticket'
    )
    return True


async def on_start_support_ticket_creation_flow(
        message: Message,
        support_ticket_repository: SupportTicketRepository,
        shop_info_repository: ShopInfoRepository,
) -> None:
    support_ticket = (
        support_ticket_repository.get_latest_support_ticket_or_none(
            user_telegram_id=message.from_user.id,
        )
    )
    if support_ticket is not None:
        check_support_ticket_create_rate_limit(
            last_ticket_created_at=support_ticket.created_at,
        )

    rules = shop_info_repository.get_value_or_none(
        key=ShopInfo.SUPPORT_RULES.name,
    )
    rules = rules or 'Rules'
    await SupportTicketCreateStates.confirm_rules.set()
    view = SupportRulesAcceptView()
    await message.answer(rules)
    await answer_view(message=message, view=view)


async def on_accept_support_rules(message: Message) -> None:
    await SupportTicketCreateStates.subject.set()
    await message.answer(
        'Enter The Subject of your inquiry'
        ' (Please make it short and without any symbols)',
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


async def on_support_ticket_issue_input(
        message: Message,
        state: FSMContext,
        user_repository: UserRepository,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    subject = state_data['subject']
    issue = message.text

    user = user_repository.get_by_telegram_id(message.from_user.id)
    support_ticket = support_ticket_repository.create(
        user_id=user.id,
        user_telegram_id=message.from_user.id,
        subject=subject,
        issue=issue,
    )

    view = SupportTicketCreatedView(support_ticket.id)
    await answer_view(message=message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_support_ticket_create_rate_limit_error,
        exception=SupportTicketCreateRateLimitError,
    )
    dispatcher.register_message_handler(
        on_start_support_ticket_creation_flow,
        Text('📋 Submit New Ticket'),
        content_types=ContentType.TEXT,
        state='*',
    )
    dispatcher.register_message_handler(
        on_accept_support_rules,
        Text('✅ I Did'),
        content_types=ContentType.TEXT,
        state=SupportTicketCreateStates.confirm_rules,
    )
    dispatcher.register_message_handler(
        on_support_ticket_subject_input,
        content_types=ContentType.TEXT,
        state=SupportTicketCreateStates.subject,
    )
    dispatcher.register_message_handler(
        on_support_ticket_issue_input,
        content_types=ContentType.TEXT,
        state=SupportTicketCreateStates.issue,
    )
