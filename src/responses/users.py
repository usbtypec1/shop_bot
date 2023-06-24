from aiogram.types import Message, CallbackQuery, ParseMode

from database import schemas
from keyboards.inline import (
    users_keyboard,
    common_keybords,
)
from keyboards.inline.callback_factories import (
    EditUserBalanceCallbackFactory
)
from responses.base import BaseResponse
from services.time_utils import get_now_datetime


class EditBalanceAlertResponse(BaseResponse):
    def __init__(self, message: Message, user: schemas.User,
                 new_balance: str, callback_data: dict[str, str]):
        self.__message = message
        self.__user = user
        self.__new_balance = new_balance
        callback_data['balance'] = new_balance
        self.__keyboard = common_keybords.ConfirmationKeyboard(
            callback_factory=EditUserBalanceCallbackFactory(),
            **callback_data,
        )

    async def _send_response(self):
        username = self.__user.username or 'user'
        text = (
            f'Are you sure you want to change the balance of {username}'
            f' with {self.__user.telegram_id}'
            f' from ${self.__user.balance} to ${self.__new_balance}?'
        )
        await self.__message.answer(text, reply_markup=self.__keyboard)


class NewBalanceResponse(BaseResponse):
    def __init__(self, query: CallbackQuery):
        self.__query = query

    async def _send_response(self):
        text = '💱 Please type the amount for the new balance:'
        await self.__query.answer()
        await self.__query.message.edit_text(text)


class IncorrectBalanceResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message

    async def _send_response(self):
        await self.__message.answer('❌ Incorrect balance!')


class BalanceEditingReasonResponse(BaseResponse):
    def __init__(self, query: CallbackQuery, callback_data: dict[str, str]):
        self.__query = query
        self.__keyboard = users_keyboard.BalanceEditingReasonsKeyboard(
            user_id=int(callback_data['user_id']),
            balance=float(callback_data['balance']),
        )

    async def _send_response(self):
        text = '❓ Enter the reason of change balance:'
        await self.__query.answer()
        await self.__query.message.edit_text(text, reply_markup=self.__keyboard)


class SuccessBalanceEditing(BaseResponse):
    def __init__(
            self,
            query: CallbackQuery,
            user: schemas.User,
            new_balance: float,
            reason: str,
    ):
        self.__query = query
        self.__user = user
        self.__new_balance = new_balance
        self.__reason = reason

    async def _send_response(self):
        # TODO Refactor it 😱
        now = get_now_datetime()
        text = (
                f'Changed balance of {self.__user.username or "user"}'
                f' with {self.__user.telegram_id} from ${self.__user.balance} to ${self.__new_balance}\n'
                f'<code>Date: {now:%m/%d/%Y}{" " * 150}' +
                (
                    f'Username: {self.__user.username}{" " * 150}' if self.__user.username is not None else '') +
                f'ID: {self.__user.telegram_id}{" " * 150}'
                f'Previous balance: {self.__user.balance}{" " * 150}'
                f'New Balance: {self.__new_balance}{" " * 150}'
                f'Reason: {self.__reason}</code>'
        )
        await self.__query.answer()
        await self.__query.message.answer(
            text=text,
            parse_mode=ParseMode.HTML,
        )
