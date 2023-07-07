from decimal import Decimal

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from common.services import render_money
from common.views import View
from payments.callback_data import (
    PaymentSystemCredentialsUpdateCallbackData,
    PaymentSystemCredentialsStatusCallbackData,
)

__all__ = (
    'UserBalanceMenuView',
    'UserBalanceTopUpPaymentMethodsView',
    'UserBalanceTopUpInvoiceView',
    'UserBalanceTopUpNotificationView',
    'PaymentManagementMenuView',
    'CoinbaseManagementMenuView',
)


class UserBalanceMenuView(View):

    def __init__(self, balance: Decimal):
        self.__balance = balance

    def get_text(self) -> str:
        return (
            f'💰 You current balance: ${render_money(self.__balance)}\n'
            'Would you like to top up your balance?'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='🔝 Top Up',
                        callback_data='start-balance-top-up-flow',
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text='🚫 Close',
                        callback_data='close',
                    ),
                ],
            ],
        )


class UserBalanceTopUpPaymentMethodsView(View):
    text = '💲 Choose payment method'
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🌐 Coinbase',
                    callback_data='coinbase',
                ),
            ],
        ],
    )


class UserBalanceTopUpInvoiceView(View):

    def __init__(
            self,
            *,
            amount_to_top_up: Decimal,
            hosted_url: str,
    ):
        self.__amount_to_top_up = amount_to_top_up
        self.__hosted_url = hosted_url

    def get_text(self) -> str:
        return (
            '<b>Currency</b>: USD\n'
            f'<b>Amount: ${render_money(self.__amount_to_top_up)}.</b>'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='🧾 Pay',
                        url=self.__hosted_url,
                    ),
                ],
            ],
        )


class UserBalanceTopUpNotificationView(View):

    def __init__(
            self,
            *,
            amount: Decimal,
            username: str | None,
            user_telegram_id: int,
    ):
        self.__amount = amount
        self.__username = username
        self.__user_telegram_id = user_telegram_id

    def get_text(self) -> str:
        if self.__username is not None:
            username = f'@{self.__username}'
        else:
            username = str(self.__user_telegram_id)
        return (
            f'✅ Balance was topped up by {render_money(self.__amount)}'
            f' by User {username}'
        )


class PaymentManagementMenuView(View):
    text = '💳 Payment Management'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('🌐 Coinbase'),
            ],
            [
                KeyboardButton('Top Up Bonuses'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class CoinbaseManagementMenuView(View):
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔑 Change API Key',
                    callback_data=(
                        PaymentSystemCredentialsUpdateCallbackData().new(
                            system='coinbase',
                        )
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text='✅ Check',
                    callback_data=(
                        PaymentSystemCredentialsStatusCallbackData().new(
                            system='coinbase',
                        )
                    ),
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🚫 Close',
                    callback_data='close',
                ),
            ],
        ],
    )

    def __init__(self, is_valid: bool = False):
        self.__is_valid = is_valid

    def get_text(self) -> str:
        status = '✅ OK' if self.__is_valid else '❌ ERROR'
        return (
            '🌐 Coinbase\n'
            f'Status: {status}'
        )
