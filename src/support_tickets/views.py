from collections.abc import Iterable

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from common.views import View
from services.time_utils import get_now_datetime
from support_tickets.callback_data import (
    SupportTicketReplyListCallbackData,
    SupportTicketReplyCreateCallbackData,
    SupportTicketAnswerUpdateCallbackData,
    SupportTicketDeleteCallbackData,
    SupportTicketStatusUpdateCallbackData,
    SupportTicketStatusListCallbackData,
    AdminSupportTicketDetailCallbackData,
    SupportTicketDetailCallbackData,
)
from support_tickets.models import (
    SupportTicket,
    SupportTicketStatus,
    SupportTicketReply,
    SupportTicketReplySource,
)

__all__ = (
    'AdminClosedSupportTicketListView',
    'AdminOpenSupportTicketListView',
    'SupportTicketStatusChangedNotificationView',
    'SupportTicketAskDeleteConfirmationView',
    'SupportTicketStatusListView',
    'AdminSupportTicketDetailView',
    'AdminSupportTicketListView',
    'SupportTicketDetailView',
    'SupportTicketListView',
    'SupportTicketCreatedView',
    'SupportRulesAcceptView',
    'SupportTicketReplyView',
    'UserSupportMenuView',
    'AdminSupportMenuView',
)


class SupportTicketStatusChangedNotificationView(View):

    def __init__(self, support_ticket: SupportTicket):
        self.__support_ticket = support_ticket

    def get_text(self) -> str:
        now = get_now_datetime()
        lines = [
            '❗️The status of your ticket was changed to'
            f' <b>{self.__support_ticket.status.value}</b>.',
            f'📆 Date: {now:%m/%d/%Y %H:%M}',
            f'🆔 Ticket Number: #{self.__support_ticket.id_display}',
            f'📱 New Status: {self.__support_ticket.status.value}',
            '📧 Message: The status of your ticket was changed to'
            f' {self.__support_ticket.status.value}.\n',
        ]
        match self.__support_ticket.status:
            case SupportTicketStatus.ON_HOLD:
                lines.append('💡 Note:')
                lines.append(
                    'For the On-Hold statuses,'
                    ' please expect longer waiting times.'
                    ' Rest assured that our team is working on your case.'
                )
            case SupportTicketStatus.PENDING:
                lines.append('💡 Note:')
                lines.append(
                    'Our team is following up your ticket.'
                    ' We will respond in few hours.'
                )
        return '\n'.join(lines)


class SupportTicketAskDeleteConfirmationView(View):
    text = '❗️ Are you sure you want to delete this ticket?'

    def __init__(self, support_ticket_id: int):
        self.__support_ticket_id = support_ticket_id

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text='Yes',
                callback_data='support-ticket-delete-confirm',
            ),
            InlineKeyboardButton(
                text='No',
                callback_data=AdminSupportTicketDetailCallbackData().new(
                    support_ticket_id=self.__support_ticket_id,
                ),
            ),
        )
        return markup


class SupportTicketStatusListView(View):
    text = 'Choose status'

    def __init__(
            self,
            *,
            support_ticket_id: int,
            current_status: SupportTicketStatus,
    ):
        self.__support_ticket_id = support_ticket_id
        self.__current_status = current_status

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        for status in SupportTicketStatus:
            if status == self.__current_status:
                continue
            markup.row(
                InlineKeyboardButton(
                    text=status.value,
                    callback_data=SupportTicketStatusUpdateCallbackData().new(
                        support_ticket_id=self.__support_ticket_id,
                        status=status.name,
                    )
                ),
            )
        return markup


class AdminSupportTicketDetailView(View):

    def __init__(self, support_ticket: SupportTicket):
        self.__support_ticket = support_ticket

    def get_text(self) -> str:
        lines = [
            f'🆔 Request number: {self.__support_ticket.id_display}',
            f'➖➖➖➖➖➖➖➖➖➖',
            f'📗 Request Subject: {self.__support_ticket.subject}',
            f'{self.__support_ticket.issue}',
            '➖➖➖➖➖➖➖➖➖➖',
            f'📱 Status: {self.__support_ticket.status.value}',
            '➖➖➖➖➖➖➖➖➖➖',
            '📧 Answer:',
            f'{self.__support_ticket.answer or ""}'
        ]
        return '\n'.join(lines)

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        if self.__support_ticket.status != SupportTicketStatus.CLOSED:
            markup.row(
                InlineKeyboardButton(
                    text='✏️ Answer',
                    callback_data=SupportTicketAnswerUpdateCallbackData().new(
                        support_ticket_id=self.__support_ticket.id,
                    ),
                ),
            )
        markup.add(
            InlineKeyboardButton(
                text='📱 Change Status',
                callback_data=SupportTicketStatusListCallbackData().new(
                    support_ticket_id=self.__support_ticket.id,
                ),
            ),
            InlineKeyboardButton(
                text='🗑 Delete Ticket',
                callback_data=SupportTicketDeleteCallbackData().new(
                    support_ticket_id=self.__support_ticket.id,
                ),
            ),
        )
        return markup


class AdminSupportTicketListView(View):
    text = 'Tickets'

    def __init__(self, support_tickets: Iterable[SupportTicket]):
        self.__support_tickets = support_tickets

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        for support_ticket in self.__support_tickets:
            text = (
                f'{support_ticket.status.value}'
                f' | #{support_ticket.id_display}'
                f' | {support_ticket.subject}'
            )
            markup.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=AdminSupportTicketDetailCallbackData().new(
                        support_ticket_id=support_ticket.id,
                    ),
                ),
            )
        return markup


class AdminOpenSupportTicketListView(AdminSupportTicketListView):
    text = '📗 Open Tickets'


class AdminClosedSupportTicketListView(AdminSupportTicketListView):
    text = '📕 Closed Tickets'


class SupportTicketDetailView(View):

    def __init__(
            self,
            *,
            support_ticket: SupportTicket,
            has_replies: bool,
    ):
        self.__support_ticket = support_ticket
        self.__has_replies = has_replies

    def get_text(self) -> str:
        lines = [
            f'🆔 Request number: #{self.__support_ticket.id_display}',
            '➖➖➖➖➖➖➖➖➖➖',
            f'📗 Request Subject: {self.__support_ticket.subject}',
            f'📋 Description: {self.__support_ticket.issue}',
            '➖➖➖➖➖➖➖➖➖➖',
        ]
        if self.__support_ticket.answer is not None:
            lines.append(f'📧 Answer: {self.__support_ticket.answer}')
            lines.append('➖➖➖➖➖➖➖➖➖➖')
        lines.append(f'📱 Status: {self.__support_ticket.status.value}')
        return '\n'.join(lines)

    def get_reply_markup(self) -> InlineKeyboardMarkup | None:
        markup = InlineKeyboardMarkup()
        if self.__support_ticket.status != SupportTicketStatus.CLOSED:
            markup.row(
                InlineKeyboardButton(
                    text='➕ Reply',
                    callback_data=SupportTicketReplyCreateCallbackData().new(
                        support_ticket_id=self.__support_ticket.id,
                    ),
                ),
            )
        if self.__has_replies:
            markup.row(
                InlineKeyboardButton(
                    text='Replies',
                    callback_data=SupportTicketReplyListCallbackData().new(
                        support_ticket_id=self.__support_ticket.id,
                    ),
                ),
            )
        if self.__support_ticket.status != SupportTicketStatus.CLOSED:
            markup.row(
                InlineKeyboardButton(
                    text='❌ Close ticket',
                    callback_data='close',
                ),
            )
        return markup


class SupportTicketListView(View):

    def __init__(self, support_tickets: Iterable[SupportTicket]):
        self.__support_tickets = tuple(support_tickets)

    def get_text(self) -> str:
        return (
            'Your support tickets' if self.__support_tickets
            else 'You have no any submitted support tickets'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        for support_ticket in self.__support_tickets:
            text = (
                f'{support_ticket.status.value}'
                f' | #{support_ticket.id_display}'
                f' | {support_ticket.subject}'
            )
            markup.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=SupportTicketDetailCallbackData().new(
                        support_ticket_id=support_ticket.id,
                    ),
                ),
            )
        return markup


class SupportTicketCreatedView(View):
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )

    def __init__(self, support_ticket_id: int):
        self.__support_ticket_id = support_ticket_id

    def get_text(self) -> str:
        return (
            'Your Support Enquiry has been sent.'
            ' We will respond within the next few hours.'
            ' Please expect delays on holidays and weekends.'
            '\nRequest number:'
            f' #{SupportTicket.to_display_id(self.__support_ticket_id)}'
        )


class SupportRulesAcceptView(View):
    text = 'Did you read the Support Rules?'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=[
            [
                KeyboardButton('✅ I Did'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class UserSupportMenuView(View):
    text = '👨‍💻 Support'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('📋 Submit New Ticket'),
                KeyboardButton('📓 Tickets'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ]
        ],
    )


class AdminSupportMenuView(View):
    text = '👨‍💻 Support'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('📗 Open Tickets'),
                KeyboardButton('📕 Closed Tickets'),
                KeyboardButton('🔎 Search'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class SupportTicketReplyView(View):

    def __init__(self, support_ticket_reply: SupportTicketReply):
        self.__support_ticket_reply = support_ticket_reply

    def get_text(self) -> str:
        match self.__support_ticket_reply.source:
            case SupportTicketReplySource.USER:
                return f'From user: {self.__support_ticket_reply.text}'
            case SupportTicketReplySource.ADMIN:
                return f'From admin: {self.__support_ticket_reply.text}'
            case _:
                raise ValueError(
                    'Invalid support ticket reply source'
                    f' {self.__support_ticket_reply.source}'
                )
