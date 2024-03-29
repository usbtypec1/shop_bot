from collections.abc import Iterable
from datetime import datetime

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from common.views import View
from time_sensitive_discounts.callback_data import (
    TimeSensitiveDiscountDetailCallbackData,
    TimeSensitiveDiscountUpdateCallbackData,
    TimeSensitiveDiscountDeleteCallbackData,
)
from time_sensitive_discounts.models import TimeSensitiveDiscount

__all__ = (
    'TimeSensitiveDiscountMenuView',
    'TimeSensitiveDiscountCreateAskForConfirmationView',
    'TimeSensitiveDiscountListView',
    'TimeSensitiveDiscountDetailView',
    'TimeSensitiveDiscountDeleteAskForConfirmationView',
    'TimeSensitiveDiscountUpdateReceiptView',
    'TimeSensitiveDiscountUpdateAskForConfirmationView',
)


class TimeSensitiveDiscountMenuView(View):
    text = '% Time Sensitive Discounts'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('Create New Discount'),
                KeyboardButton('View Active Discounts'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class TimeSensitiveDiscountCreateAskForConfirmationView(View):

    def __init__(
            self,
            *,
            starts_at: datetime,
            expires_at: datetime,
    ):
        self.__starts_at = starts_at
        self.__expires_at = expires_at

    def get_text(self) -> str:
        text = (
            'Are you sure you want to create a discount which begins in'
            f' {self.__starts_at:%m/%d/%Y %H:%M} and'
        )
        if self.__expires_at is None:
            text += ' never finishes'
        else:
            text += f' finishes in {self.__expires_at:%m/%d/%Y %H:%M}'
        return text

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='time-sensitive-discount-create-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data='show-time-sensitive-discount-list',
                    ),
                ],
            ],
        )


class TimeSensitiveDiscountListView(View):

    def __init__(
            self,
            time_sensitive_discounts: Iterable[TimeSensitiveDiscount],
    ):
        self.__time_sensitive_discounts = tuple(time_sensitive_discounts)

    def get_text(self) -> str:
        return (
            'Time Sensitive Discounts' if self.__time_sensitive_discounts
            else 'No Time Sensitive Discounts available'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for time_sensitive_discount in self.__time_sensitive_discounts:
            text = (
                f'#{time_sensitive_discount.id}'
                f' - {time_sensitive_discount.code}'
            )
            markup.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=TimeSensitiveDiscountDetailCallbackData().new(
                        time_sensitive_discount_id=time_sensitive_discount.id,
                    ),
                ),
            )

        return markup


class TimeSensitiveDiscountDetailView(View):

    def __init__(self, time_sensitive_discount: TimeSensitiveDiscount):
        self.__time_sensitive_discount = time_sensitive_discount

    def get_text(self) -> str:
        starts_at = f'{self.__time_sensitive_discount.starts_at:%m/%d/%Y %H:%M}'
        text = (
            f'<b>Code:</b> {self.__time_sensitive_discount.code}\n'
            f'<b>Will be started at:</b> {starts_at}\n'
        )
        if self.__time_sensitive_discount.expires_at is not None:
            text += (
                f'<b>Will be ended at:</b>'
                f' {self.__time_sensitive_discount.expires_at:%m/%d/%Y %H:%M}'
            )
        return text

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='📝 Edit',
                        callback_data=(
                            TimeSensitiveDiscountUpdateCallbackData().new(
                                time_sensitive_discount_id=(
                                    self.__time_sensitive_discount.id
                                ),
                            )
                        ),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text='🗑️ Delete',
                        callback_data=(
                            TimeSensitiveDiscountDeleteCallbackData().new(
                                time_sensitive_discount_id=(
                                    self.__time_sensitive_discount.id
                                ),
                            )
                        ),
                    ),
                ],
            ]
        )


class TimeSensitiveDiscountDeleteAskForConfirmationView(View):
    text = '❓ Are you sure you want to delete this time sensitive discount?'

    def __init__(self, time_sensitive_discount_id: int):
        self.__time_sensitive_discount_id = time_sensitive_discount_id

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='time-sensitive-discount-delete-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data=(
                            TimeSensitiveDiscountDetailCallbackData().new(
                                time_sensitive_discount_id=(
                                    self.__time_sensitive_discount_id
                                ),
                            )
                        ),
                    ),
                ],
            ],
        )


class TimeSensitiveDiscountUpdateAskForConfirmationView(View):

    def __init__(
            self,
            *,
            starts_at: datetime,
            expires_at: datetime,
            time_sensitive_discount_id: int,
    ):
        self.__starts_at = starts_at
        self.__expires_at = expires_at
        self.__time_sensitive_discount_id = time_sensitive_discount_id

    def get_text(self) -> str:
        text = (
            'Are you sure you want to edit a discount which begins in'
            f' {self.__starts_at:%m/%d/%Y %H:%M} and'
        )
        if self.__expires_at is None:
            text += ' never finishes'
        else:
            text += f' finishes in {self.__expires_at:%m/%d/%Y %H:%M}'
        return text

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='time-sensitive-discount-update-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data=(
                            TimeSensitiveDiscountDetailCallbackData().new(
                                time_sensitive_discount_id=(
                                    self.__time_sensitive_discount_id
                                ),
                            )
                        ),
                    ),
                ],
            ],
        )


class TimeSensitiveDiscountUpdateReceiptView(View):

    def __init__(
            self,
            *,
            old_discount_code: str,
            new_discount_code: str,
            new_discount_value: int,
            new_starts_at: datetime | None,
            new_expires_at: datetime | None,
    ):
        self.__old_discount_code = old_discount_code
        self.__new_discount_code = new_discount_code
        self.__new_discount_value = new_discount_value
        self.__new_starts_at = new_starts_at
        self.__new_expires_at = new_expires_at

    def get_text(self) -> str:
        if self.__new_starts_at is None:
            starts_at = 'Now'
        else:
            starts_at = f'{self.__new_starts_at:%m/%d/%Y %H:%M}'

        if self.__new_expires_at is None:
            expires_at = 'infinite'
        else:
            expires_at = f'{self.__new_expires_at:%m/%d/%Y %H:%M}'

        return (
            '<code>'
            f'Old Discount Code: {self.__old_discount_code}\n'
            f'New Discount Code: {self.__new_discount_code}\n'
            f'New Discounted Amount: {self.__new_discount_value}%\n'
            f'New Start Date: {starts_at}\n'
            f'New Finish Date: {expires_at}'
            '</code>'
        )
