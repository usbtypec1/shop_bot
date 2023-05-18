from aiogram.types import Message, CallbackQuery, ParseMode

from keyboards.inline import (
    users_keyboard,
    common_keybords,
)
from keyboards.inline.callback_factories import (
    UserCallbackFactory,
    EditUserBalanceCallbackFactory,
    TopUpUserBalanceCallbackFactory
)
from responses.base import BaseResponse
from services.db_api import schemas
from services.time_utils import get_now_datetime


class UsersResponse(BaseResponse):
    def __init__(
            self,
            update: CallbackQuery | Message,
            users: list[schemas.User],
            total_balance: float,
            users_filter: str = '',
            page: int = 0,
            page_size: int = 10,
            callback_data: dict[str, str] | None = None,
    ):
        self.__update = update
        self.__keyboard = users_keyboard.UsersKeyboard(
            users=users,
            page=page,
            page_size=page_size,
            users_filter=users_filter,
            callback_data=callback_data,
        )
        self.__users_quantity = len(users)
        self.__total_balance = total_balance
        self.__page = page
        self.__page_size = page_size

    async def _send_response(self):
        total_balance = self.__total_balance or 0.0
        text = (
            f"Total Users: {self.__users_quantity}\n"
            f"Total Balances in User's profiles: ${total_balance}"
        )
        match self.__update:
            case CallbackQuery():
                await self.__update.answer()
                await self.__update.message.edit_text(
                    text=text,
                    reply_markup=self.__keyboard,
                )
            case Message():
                await self.__update.answer(text, reply_markup=self.__keyboard)


class UserResponse(BaseResponse):
    def __init__(
            self,
            query: CallbackQuery,
            user: schemas.User,
            number_of_orders: int,
            callback_data: dict[str, str] | None = None,
    ):
        self.__query = query
        self.__user = user
        self.__number_of_orders = number_of_orders
        if callback_data is None:
            callback_data = {
                '@': 'users',
                'filter': '',
                'page': '0',
                'id': user.id,
                'action': 'manage',
                'is_confirmed': '',
            }
        else:
            callback_data['is_confirmed'] = ''
        self.__keyboard = users_keyboard.UserKeyboard(
            user_id=user.id,
            is_user_banned=user.is_banned,
            callback_data=callback_data,
        )

    async def _send_response(self):
        username = self.__user.username or ''
        banned_status = 'banned' if self.__user.is_banned else 'not banned'
        registered_at = f'{self.__user.created_at:%m/%d/%Y}'
        text = (
                f'<b>User ID</b>: {self.__user.telegram_id}\n'
                f'<b>Username</b>: @{username}\n'
                f'<b>Registration Date</b>: {registered_at}\n'
                f'<b>Number of orders</b>: {self.__number_of_orders}\n'
                f'<b>Balance</b>: ${self.__user.balance}\n\n'
                f'<b>Status</b>: {banned_status}'
        )
        await self.__query.answer()
        await self.__query.message.edit_text(
            text=text,
            reply_markup=self.__keyboard,
            parse_mode=ParseMode.HTML,
        )


class SearchUserResponse(BaseResponse):
    def __init__(self, query: CallbackQuery):
        self.__query = query

    async def _send_response(self):
        text = '🆔 Enter usernames or ids'
        await self.__query.answer()
        await self.__query.message.edit_text(text)


class FoundUsersResponse(BaseResponse):
    def __init__(self, message: Message):
        self.__message = message

    async def _send_response(self) -> Message:
        return await self.__message.answer(
            f'🔡 Found users with these usernames'
            f' and ids: {self.__message.text}'
        )


class BanUserAlertResponse(BaseResponse):
    def __init__(self, query: CallbackQuery, user: schemas.User,
                 callback_data: dict[str, str]):
        self.__query = query
        self.__user = user
        self.__keyboard = common_keybords.ConfirmationKeyboard(
            callback_factory=UserCallbackFactory(),
            **callback_data,
        )

    async def _send_response(self):
        await self.__query.answer()
        await self.__query.message.edit_text(
            f'Are you sure you want to ban '
            f'{self.__user.username if self.__user.username is not None else "user"} '
            f'with {self.__user.telegram_id}?',
            reply_markup=self.__keyboard
        )


class UnbanUserAlertResponse(BaseResponse):
    def __init__(
            self,
            query: CallbackQuery,
            user: schemas.User,
            callback_data: dict[str, str],
    ):
        self.__query = query
        self.__user = user
        self.__keyboard = common_keybords.ConfirmationKeyboard(
            callback_factory=UserCallbackFactory(),
            **callback_data,
        )

    async def _send_response(self):
        username = self.__user.username or 'user'
        await self.__query.answer()
        await self.__query.message.edit_text(
            f'Are you sure you want to unban {username} '
            f'with {self.__user.telegram_id}?',
            reply_markup=self.__keyboard
        )


class DeleteUserAlert(BaseResponse):
    def __init__(
            self,
            query: CallbackQuery,
            user: schemas.User,
            callback_data: dict[str, str],
    ):
        self.__query = query
        self.__user = user
        self.__keyboard = common_keybords.ConfirmationKeyboard(
            callback_factory=UserCallbackFactory(),
            **callback_data,
        )

    async def _send_response(self):
        text = (
            f'This user has ${self.__user.balance} left.'
            f' Are you sure you want to delete this user?'
        )
        await self.__query.answer()
        await self.__query.message.edit_text(text, reply_markup=self.__keyboard)


class SuccessUserRemovalResponse(BaseResponse):
    def __init__(self, query: CallbackQuery, user: schemas.User):
        self.__user = user
        self.__query = query

    async def _send_response(self) -> Message:
        username = self.__user.username or 'user'
        text = (
            f'✅ Deleted {username} with {self.__user.telegram_id}'
            f' and previous balance of {self.__user.balance}'
        )
        await self.__query.answer()
        return await self.__query.message.edit_text(text=text)


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


class TopUpBalanceAlertResponse(BaseResponse):
    def __init__(
            self,
            message: Message,
            user: schemas.User,
            balance: str,
            callback_data: dict[str, str],
    ):
        self.__message = message
        self.__user = user
        self.__balance = balance
        callback_data['balance_delta'] = balance
        self.__keyboard = common_keybords.ConfirmationKeyboard(
            callback_factory=TopUpUserBalanceCallbackFactory(),
            **callback_data,
        )

    async def _send_response(self):
        username = self.__user.username or 'user'
        text = (
            f'Are you sure you want to top-up the balance of {username}'
            f' with {self.__user.telegram_id} for ${self.__balance}?'
        )
        await self.__message.answer(text, reply_markup=self.__keyboard)


class BalanceRefillMethodResponse(BaseResponse):
    def __init__(
            self,
            query: CallbackQuery,
            callback_data: dict[str, str],
    ):
        self.__query = query
        self.__keyboard = users_keyboard.BalanceRefillMethodsKeyboard(
            user_id=int(callback_data['user_id']),
            balance=float(callback_data['balance_delta']),
        )

    async def _send_response(self):
        text = '❓ Enter the manual payment method the user paid:'
        await self.__query.answer()
        await self.__query.message.edit_text(text, reply_markup=self.__keyboard)


class SuccessBalanceRefillResponse(BaseResponse):
    def __init__(
            self,
            query: CallbackQuery,
            user: schemas.User,
            balance_delta: float,
            method: str,
    ):
        self.__query = query
        self.__user = user
        self.__balance_delta = balance_delta
        self.__method = method

    async def _send_response(self):
        # TODO Refactor it too 😱
        now = get_now_datetime()
        text = (
                f'Topped-up {self.__user.username or "user"} '
                f'with {self.__user.telegram_id} for ${self.__balance_delta}\n'
                f'<code>Date: {now:%m/%d/%Y}{150 * " "}' +
                (
                    f'Username: {self.__user.username}{150 * " "}' if self.__user.username is not None else '') +
                f'ID: {self.__user.telegram_id}{150 * " "}'
                f'Topped Up amount: {self.__balance_delta}{150 * " "}'
                f'Total Balance: {self.__user.balance}{150 * " "}'
                f'Method of payment: {self.__method}</code>'
        )
        await self.__query.answer()
        await self.__query.message.answer(text)
