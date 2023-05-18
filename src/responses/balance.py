from aiogram.types import Message, CallbackQuery

from keyboards.buttons import common_buttons
from keyboards.inline import balance_keyboards, payments_keyboards
from keyboards.inline.callback_factories import TopUpBalanceCallbackFactory
from responses.base import BaseResponse


class BalanceResponse(BaseResponse):

    def __init__(self, message: Message, balance: float):
        self.__message = message
        self.__balance = balance
        self.__keyboard = balance_keyboards.TopUpBalanceKeyboard()

    async def _send_response(self):
        await self.__message.answer(
            text=(
                f'⚖️ You current balance: ${self.__balance}\n'
                f'Do you want top up it?'
            ),
            reply_markup=self.__keyboard,
        )


class BalanceAmountResponse(BaseResponse):
    def __init__(self, query: CallbackQuery):
        self.__query = query

    async def _send_response(self):
        await self.__query.answer()
        await self.__query.message.edit_text('🔢 Enter amount')


class IncorrectBalanceAmountResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('💯 Incorrect balance amount!')


class PaymentMethodResponse(BaseResponse):
    def __init__(self, message: Message, callback_data: dict[str: str],
                 crypto_payments: str = None):
        self.__message = message
        callback_data.pop('@')
        self.__keyboard = payments_keyboards.PaymentMethodsKeyboard(
            callback_data=callback_data,
            callback_factory=TopUpBalanceCallbackFactory(),
            crypto_payments=crypto_payments
        )
        self.__keyboard.add(common_buttons.CloseButton())

    async def _send_response(self):
        await self.__message.answer(
            text='💲 Choose payment method',
            reply_markup=self.__keyboard,
        )


class SuccessBalanceRefillResponse(BaseResponse):
    def __init__(self, query: CallbackQuery, amount: float):
        self.__query = query
        self.__amount = amount

    async def _send_response(self):
        await self.__query.message.delete()
        await self.__query.message.answer(
            text=f'✅ Balance was topped up by {self.__amount}',
        )


class FailedBalanceRefillResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.edit_text(text='🚫 Balance refill failed')
