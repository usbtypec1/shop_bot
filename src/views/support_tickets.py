from collections.abc import Iterable

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import models
from keyboards.inline.callback_factories import SupportTicketDetailCallbackData
from views.base import View

__all__ = (
    'SupportTicketDetailView',
    'SupportTicketListView',
    'SupportTicketCreatedView',
    'SupportRulesAcceptView',
    'UserSupportMenuView',
    'AdminSupportMenuView',
)


class SupportTicketDetailView(View):

    def __init__(self, support_ticket: models.SupportTicket):
        self.__support_ticket = support_ticket

    def get_text(self) -> str:
        lines = [
            f'🆔 Request number: #{self.__support_ticket.id}',
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
        if self.__support_ticket.status != models.SupportTicketStatus.CLOSED:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton(
                    text='➕ Reply',
                    callback_data='reply'
                ),
                InlineKeyboardButton(
                    text='❌ Close ticket',
                    callback_data='close',
                ),
            )
            return markup


class SupportTicketListView(View):

    def __init__(self, support_tickets: Iterable[models.SupportTicket]):
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
                f' | #{support_ticket.id}'
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
            f'\nRequest number: #{self.__support_ticket_id}'
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
                KeyboardButton('📗 Open Ticket'),
                KeyboardButton('📕 Closed Ticket'),
                KeyboardButton('🔎 Search'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )
