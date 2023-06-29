from decimal import Decimal

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.views import View

__all__ = (
    'UserBalanceMenuView',
    'UserBalanceTopUpPaymentMethodsView',
    'UserBalanceTopUpInvoiceView',
    'UserBalanceTopUpNotificationView',
)


class UserBalanceMenuView(View):

    def __init__(self, balance: Decimal):
        self.__balance = balance

    def get_text(self) -> str:
        return (
            f'💰 You current balance: ${self.__balance:.2f}\n'
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
            f'<b>Amount: ${self.__amount_to_top_up:.2f}.</b>'
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
        return f'✅ Balance was topped up by {self.__amount} by User {username}'
