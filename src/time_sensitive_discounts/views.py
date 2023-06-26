from collections.abc import Iterable
from datetime import datetime

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from common.views import View

__all__ = (
    'TimeSensitiveDiscountMenuView',
    'TimeSensitiveDiscountAskForConfirmationView',
    'TimeSensitiveDiscountListView',
)

from time_sensitive_discounts.callback_data import \
    TimeSensitiveDiscountDetailCallbackData

from time_sensitive_discounts.models import TimeSensitiveDiscount


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


class TimeSensitiveDiscountAskForConfirmationView(View):

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
                        callback_data='dev',
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
