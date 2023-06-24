from decimal import Decimal
from typing import Protocol

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from common.models import Buyer
from common.views import View
from keyboards.inline.callback_factories import (
    UserCallbackFactory,
)
from services.time_utils import get_now_datetime
from users.callback_data import (
    UserDetailCallbackData,
    UserDeleteCallbackData,
    UserUpdateCallbackData,
    UserBalanceTopUpCallbackData, UserSetSpecificBalanceCallbackData,
)
from users.models import User

__all__ = (
    'RulesView',
    'UserMenuView',
    'AdminMenuView',
    'UserGreetingsView',
    'UserStatisticsMenuView',
    'UserGeneralStatisticsView',
    'UserListView',
    'NewUserNotificationView',
    'UserDetailView',
    'UserDeleteAskForConfirmationView',
    'UserDeleteSuccessView',
    'UserBannedStatusToggleView',
    'UserBalanceTopUpReceiptView',
    'UserBalanceTopUpAskForConfirmationView',
    'UserSetSpecificBalanceAskForConfirmationView',
    'UserSetSpecificBalanceReceiptView',
    'UserSetSpecificBalanceReasonsView',
)


class HasId(Protocol):
    id: int


class HasBalance(Protocol):
    balance: Decimal


class HasTelegramIdAndUsername(Protocol):
    telegram_id: int
    username: str | None


class HasIdAndBalance(HasId, HasBalance, Protocol):
    pass


class HasIdAndTelegramIdAndUsername(HasId, HasTelegramIdAndUsername, Protocol):
    pass


class HasIdAndTelegramIdAndUsernameAndBannedStatus(
    HasIdAndTelegramIdAndUsername,
    Protocol,
):
    is_banned: bool


class HasTelegramIdAndUsernameAndBalance(
    HasTelegramIdAndUsername,
    HasBalance,
    Protocol,
):
    pass


class RulesView(View):
    text = 'Rules'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('✅ Accept'),
            ],
        ],
    )


class UserMenuView(View):
    text = '🔹 Main Menu 🔹'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('🛒 Products'),
            ],
            [
                KeyboardButton('ℹ️ FAQ'),
                KeyboardButton('📗 Rules'),
                KeyboardButton('💲 Balance'),
            ],
            [
                KeyboardButton('📱 Profile'),
                KeyboardButton('🛒 Cart'),
                KeyboardButton('👨‍💻 Support'),
            ],
        ],
    )


class AdminMenuView(View):
    text = '🔹 Main Menu 🔹'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('🛒 Products'),
                KeyboardButton('🗂 Mng Categories & Prod'),
                KeyboardButton('💳 Payment Management'),
            ],
            [
                KeyboardButton('🏪 Shop Information'),
                KeyboardButton('🛒 Cart'),
                KeyboardButton('💲 Balance'),
            ],
            [
                KeyboardButton('📊 Statistics'),
                KeyboardButton('🙍‍♂ Users'),
                KeyboardButton('📧 Newsletter'),
            ],
            [
                KeyboardButton('👨‍💻 Support'),
                KeyboardButton('💾 Backup'),
            ],
        ],
    )


class UserGreetingsView(View):

    def __init__(self, full_name: str):
        self.__full_name = full_name

    def get_text(self) -> str:
        return f'Hello {self.__full_name}!'


class UserStatisticsMenuView(View):
    text = '📊 Statistics'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('📊 General'),
                KeyboardButton('📆 Daily'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class UserGeneralStatisticsView(View):

    def __init__(
            self,
            *,
            buyers_count: int,
            orders_total_cost: float,
            sold_products_count: int,
            sold_product_units_quantity: list[tuple[str, int, ...]],
            active_buyers: list[Buyer],
    ):
        self.__buyers_count = buyers_count
        self.__orders_total_cost = orders_total_cost
        self.__sold_products_count = sold_products_count
        self.__sold_product_units_quantity = sold_product_units_quantity
        self.__active_buyers = active_buyers

    def get_text(self) -> str:
        lines = [
            f'🙍‍♂ Number of buyers: {self.__buyers_count}'
            '➖➖➖➖➖➖➖➖➖➖',
            f'🛒 Number of purchased items: {self.__sold_products_quantity}',
            '\n',
        ]
        lines += [
            f'▫️ {name} - {quantity}'
            for name, quantity, _ in self.__sold_product_units_quantity
        ]
        lines += [
            '➖➖➖➖➖➖➖➖➖➖',
            '🙍‍♂ Active buyers:',
            '\n',
        ]
        for buyer in self.__active_buyers:
            username = buyer['username'] or ''
            lines.append(
                f'{buyer["telegram_id"]}|@{username}'
                f'|{buyer["purchase_number"]}{buyer["orders_amount"]}'
            )
        lines.append('➖➖➖➖➖➖➖➖➖➖')

        return '\n'.join(lines)


class UserListView(View):

    def __init__(
            self,
            *,
            users: list[User],
            total_balance: Decimal,
            users_filter: str = '',
            page: int = 0,
            page_size: int = 10,
            callback_data: dict[str, str] | None = None,
    ):
        self.__total_balance = total_balance
        self.__page = page
        self.__users = users
        self.__page_size = page_size
        self.__callback_data = callback_data
        self.__users_filter = users_filter

    def get_text(self) -> str:
        return (
            f"Total Users: {len(self.__users)}\n"
            f"Total Balances in User's profiles: ${self.__total_balance}"
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for user in self.__users:
            markup.row(
                InlineKeyboardButton(
                    text=(
                        f'#{user.telegram_id}'
                        f' | {user.username}'
                        f' | ${user.balance:.2f}'
                        f' | {user.created_at:%m/%d/%Y}'
                    ),
                    callback_data=UserDetailCallbackData().new(
                        user_id=user.id,
                    ),
                )
            )
        if not self.__users_filter:
            markup.row(
                InlineKeyboardButton(
                    text='🔎 Search Users',
                    callback_data='search-users',
                )
            )
        else:
            markup.row(
                InlineKeyboardButton(
                    text='⬅️ Back',
                    callback_data=UserCallbackFactory().new(
                        filter='',
                        page=self.__page,
                        id='',
                        action='',
                        is_confirmed='',
                    )
                )
            )
        if len(self.__users) > self.__page_size:
            markup.row(
                InlineKeyboardButton(
                    text='Next 👉',
                    callback_data=UserCallbackFactory().new(
                        filter=self.__users_filter,
                        page=self.__page + 1,
                        id='',
                        action='',
                        is_confirmed='',
                    )
                )
            )
        if self.__page > 0:
            markup.row(
                InlineKeyboardButton(
                    text='👈 Previous',
                    callback_data=UserCallbackFactory().new(
                        filter=self.__users_filter,
                        page=self.__page - 1,
                        id='',
                        action='',
                        is_confirmed='',
                    )
                )
            )
        markup.row(
            InlineKeyboardButton(
                text='🚫 Close',
                callback_data='close',
            )
        )
        return markup


class UserDetailView(View):

    def __init__(
            self,
            *,
            user: User,
            number_of_orders: int,
    ):
        self.__user = user
        self.__number_of_orders = number_of_orders

    def get_text(self) -> str:
        username = self.__user.username or ''
        banned_status = 'banned' if self.__user.is_banned else 'not banned'
        registered_at = f'{self.__user.created_at:%m/%d/%Y}'
        return (
            f'<b>User ID</b>: {self.__user.telegram_id}\n'
            f'<b>Username</b>: @{username}\n'
            f'<b>Registration Date</b>: {registered_at}\n'
            f'<b>Number of orders</b>: {self.__number_of_orders}\n'
            f'<b>Balance</b>: ${self.__user.balance:.2f}\n\n'
            f'<b>Status</b>: {banned_status}'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text='⚖️ Edit Balance',
                callback_data=UserSetSpecificBalanceCallbackData().new(
                    user_id=self.__user.id,
                ),
            ),
            InlineKeyboardButton(
                text='💸 Top Up Balance',
                callback_data=UserBalanceTopUpCallbackData().new(
                    user_id=self.__user.id,
                ),
            ),
        )
        markup.row(
            InlineKeyboardButton(
                text='🫥 Delete User',
                callback_data=UserDeleteCallbackData().new(
                    user_id=self.__user.id
                ),
            ),
        )
        markup.row(
            InlineKeyboardButton(
                text=f'🆓 Unban' if self.__user.is_banned else f'📛 Ban',
                callback_data=UserUpdateCallbackData().new(
                    user_id=self.__user.id,
                    field='banned-status',
                )
            )
        )
        markup.row(
            InlineKeyboardButton(
                text='🚫 Close',
                callback_data='close',
            )
        )
        return markup


class NewUserNotificationView(View):

    def __init__(self, *, telegram_id: int, username: str | None = None):
        self.__telegram_id = telegram_id
        self.__username = username

    def get_text(self) -> str:
        username = self.__username or ''
        return (
            '📱 New user\n'
            '➖➖➖➖➖➖➖➖➖➖\n'
            f'🙍‍♂ Name: @{username}\n'
            f'🆔 ID: {self.__telegram_id}'
        )


class UserDeleteAskForConfirmationView(View):

    def __init__(self, user: HasIdAndBalance):
        self.__user = user

    def get_text(self) -> str:
        return (
            f'This user has ${self.__user.balance:.2f} left.'
            f' Are you sure you want to delete this user?'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='user-delete-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data=UserDetailCallbackData().new(
                            user_id=self.__user.id,
                        ),
                    )
                ],
            ],
        )


class UserDeleteSuccessView(View):

    def __init__(self, user: HasTelegramIdAndUsernameAndBalance):
        self.__user = user

    def get_text(self) -> str:
        username = self.__user.username or 'user'
        return (
            f'✅ Deleted {username} with ID {self.__user.telegram_id}'
            f' and previous balance of {self.__user.balance:.2f}'
        )


class UserBannedStatusToggleView(View):

    def __init__(self, user: HasIdAndTelegramIdAndUsernameAndBannedStatus):
        self.__user = user

    def get_text(self) -> str:
        username = self.__user.username or 'user'
        toggle_text = 'unban' if self.__user.is_banned else 'ban'
        return (
            f'Are you sure you want to <b><u>{toggle_text}</u></b>'
            f' {username} with {self.__user.telegram_id}?'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='banned-status-toggle-confirm'
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data=UserDetailCallbackData().new(
                            user_id=self.__user.id,
                        )
                    ),
                ],
            ],
        )
        return markup


class UserBalanceTopUpAskForConfirmationView(View):

    def __init__(
            self,
            *,
            user: HasIdAndTelegramIdAndUsernameAndBannedStatus,
            amount_to_top_up: Decimal,
            payment_method: str,
    ):
        self.__user = user
        self.__amount_to_top_up = amount_to_top_up
        self.__payment_method = payment_method

    def get_text(self) -> str:
        username = self.__user.username or 'user'
        return (
            f'Are you sure you want to top-up {username}\'s balance'
            f' with Telegram ID {self.__user.telegram_id}'
            f' for ${self.__amount_to_top_up}?\n'
            f'Method of payment: {self.__payment_method}'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='top-up-user-balance-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data=UserDetailCallbackData().new(
                            user_id=self.__user.id,
                        )
                    ),
                ],
            ],
        )


class UserBalanceTopUpReceiptView(View):

    def __init__(
            self,
            *,
            user: HasTelegramIdAndUsernameAndBalance,
            amount_to_top_up: Decimal,
            payment_method: str,
    ):
        self.__user = user
        self.__amount_to_top_up = amount_to_top_up
        self.__payment_method = payment_method

    def get_text(self) -> str:
        now = get_now_datetime()

        # I don't know why each line ends with 150 * " " expression
        username = f'{self.__user.username}{150 * " "}' or ''
        return (
            f'Topped-up {self.__user.username or "user"}'
            f' with Telegram ID {self.__user.telegram_id}'
            f' for ${self.__amount_to_top_up}\n'
            f'<code>Date: {now:%m/%d/%Y}{150 * " "}'
            f'Username: {username}'
            f'ID: {self.__user.telegram_id}{150 * " "}'
            f'Topped Up amount: {self.__amount_to_top_up}{150 * " "}'
            f'Total Balance: {self.__user.balance:.2f}{150 * " "}'
            f'Method of payment: {self.__payment_method}</code>'
        )


class UserSetSpecificBalanceAskForConfirmationView(View):

    def __init__(
            self,
            *,
            user: HasIdAndTelegramIdAndUsername,
            amount_to_set: Decimal,
            reason: str,
    ):
        self.__user = user
        self.__amount_to_set = amount_to_set
        self.__reason = reason

    def get_text(self) -> str:
        username = self.__user.username or 'user'
        return (
            f'Are you sure you want to change {username}\'s balance'
            f' with Telegram ID {self.__user.telegram_id}'
            f' for ${self.__amount_to_set}?\n'
            f'Reason: {self.__reason}'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='set-specific-user-balance-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data=UserDetailCallbackData().new(
                            user_id=self.__user.id,
                        )
                    ),
                ],
            ],
        )


class UserSetSpecificBalanceReceiptView(View):

    def __init__(
            self,
            *,
            user: HasTelegramIdAndUsernameAndBalance,
            old_balance: Decimal,
            new_balance: Decimal,
            reason: str,
    ):
        self.__user = user
        self.__old_balance = old_balance
        self.__new_balance = new_balance
        self.__reason = reason

    def get_text(self) -> str:
        now = get_now_datetime()

        # I don't know why each line ends with 150 * " " expression
        username = f'{self.__user.username}{150 * " "}' or ''
        return (
            f'Changed balance of {self.__user.username or "user"}'
            f' with Telegram ID {self.__user.telegram_id}'
            f' from ${self.__old_balance:.2f} to ${self.__new_balance:.2f}\n'
            f'<code>Date: {now:%m/%d/%Y}{150 * " "}'
            f'Username: {username}'
            f'ID: {self.__user.telegram_id}{150 * " "}'
            f'Previous balance: {self.__old_balance:.2f}{" " * 150}'
            f'New Balance: {self.__new_balance:.2f}{" " * 150}'
            f'Reason: {self.__reason}</code>'
        )


class UserSetSpecificBalanceReasonsView(View):
    text = '❓ Enter the reason of change balance'
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🤝 P2P Delivery',
                    callback_data='P2P Delivery',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🔄 Refunded Payment',
                    callback_data='Refunded Payment',
                ),
            ],
            [
                InlineKeyboardButton(
                    text='🫤 Admin Mistake',
                    callback_data='Admin Mistake',
                ),
            ],
        ]
    )
