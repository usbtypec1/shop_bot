from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import (
    Message,
    ContentType,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)

from common.filters import AdminFilter
from common.views import answer_view
from database.schemas import SupportTicketStatus
from services.validators import validate_date_range
from support_tickets.exceptions import InvalidSupportDateRangeError
from support_tickets.repositories import SupportTicketRepository
from support_tickets.states import SupportTicketSearchStates
from support_tickets.views import AdminSupportTicketListView


async def on_start_support_ticket_search_flow(
        message: Message,
) -> None:
    await SupportTicketSearchStates.user_id.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Skip', callback_data='skip-user-id'))
    await message.answer(
        'Please enter Username or Telegram ID of the User'
        ' you want to show their tickets',
        reply_markup=markup,
    )


async def on_user_telegram_id_or_username_skip(
        callback_query: CallbackQuery,
) -> None:
    await SupportTicketSearchStates.date_range.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Skip', callback_data='skip-date-range'))
    await callback_query.message.answer(
        'Enter the Date Range ticket was sent (Format: MM/DD/YYYY-MM/DD/YYYY)',
        reply_markup=markup,
    )


async def on_user_telegram_id_or_username_input(
        message: Message,
        state: FSMContext,
) -> None:
    if message.text.isdigit():
        await state.update_data(user_telegram_id=int(message.text))
    else:
        await state.update_data(username=message.text)
    await SupportTicketSearchStates.date_range.set()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Skip', callback_data='skip-date-range'))
    await message.answer(
        'Enter the Date Range ticket was sent (Format: MM/DD/YYYY-MM/DD/YYYY)',
        reply_markup=markup,
    )


async def on_date_range_skip(
        callback_query: CallbackQuery,
) -> None:
    await SupportTicketSearchStates.status.set()
    markup = InlineKeyboardMarkup()
    markup.add(
        *(
            InlineKeyboardButton(
                text=support_ticket_status.value,
                callback_data=support_ticket_status.name,
            ) for support_ticket_status in SupportTicketStatus
        )
    )
    await callback_query.message.answer(
        text='Choose the status you want to see',
        reply_markup=markup,
    )


async def on_invalid_support_date_range_error(
        update: Update,
        _: InvalidSupportDateRangeError,
) -> bool:
    await update.message.answer(
        'Invalid date range'
        '\n(Format: MM/DD/YYYY-MM/DD/YYYY)'
    )
    await SupportTicketSearchStates.date_range.set()
    return True


async def on_date_range_input(
        message_or_callback_query: Message | CallbackQuery,
        state: FSMContext,
) -> None:
    await SupportTicketSearchStates.status.set()
    match message_or_callback_query:
        case Message() as message:
            period = validate_date_range(message.text)
            await state.update_data(period=period)
        case CallbackQuery() as callback_query:
            message = callback_query.message
        case _:
            raise
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        *(
            InlineKeyboardButton(
                text=support_ticket_status.value,
                callback_data=support_ticket_status.name,
            ) for support_ticket_status in SupportTicketStatus
        )
    )
    await message.answer(
        text='Choose the status you want to see',
        reply_markup=markup,
    )


async def on_support_ticket_status_choice(
        callback_query: CallbackQuery,
        state: FSMContext,
        support_ticket_repository: SupportTicketRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()

    status = SupportTicketStatus[callback_query.data]
    user_telegram_id = state_data.get('user_telegram_id')
    username = state_data.get('username')
    period = state_data.get('period')

    support_tickets = support_ticket_repository.get_support_tickets_by_filter(
        status=status,
        period=period,
        user_telegram_id=user_telegram_id,
        username=username,
    )
    if not support_tickets:
        await callback_query.message.answer(
            '😔 No results found for your query'
        )
        return
    view = AdminSupportTicketListView(support_tickets)
    await callback_query.message.answer('Here is the list of the tickets:')
    await answer_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_start_support_ticket_search_flow,
        Text('🔎 Search'),
        AdminFilter(),
        content_types=ContentType.TEXT,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_user_telegram_id_or_username_skip,
        Text('skip-user-id'),
        AdminFilter(),
        state=SupportTicketSearchStates.user_id,
    )
    dispatcher.register_message_handler(
        on_user_telegram_id_or_username_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=SupportTicketSearchStates.user_id,
    )
    dispatcher.register_callback_query_handler(
        on_date_range_skip,
        Text('skip-date-range'),
        AdminFilter(),
        state=SupportTicketSearchStates.user_id,
    )
    dispatcher.register_errors_handler(
        on_invalid_support_date_range_error,
        exception=InvalidSupportDateRangeError,
    )
    dispatcher.register_callback_query_handler(
        on_date_range_input,
        AdminFilter(),
        state=SupportTicketSearchStates.date_range,
    )
    dispatcher.register_message_handler(
        on_date_range_input,
        AdminFilter(),
        content_types=ContentType.TEXT,
        state=SupportTicketSearchStates.date_range,
    )
    dispatcher.register_callback_query_handler(
        on_support_ticket_status_choice,
        AdminFilter(),
        state=SupportTicketSearchStates.status,
    )
