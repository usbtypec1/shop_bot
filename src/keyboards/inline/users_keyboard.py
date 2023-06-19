import aiogram.types

from keyboards.buttons import users_buttons, navigation_buttons, common_buttons
from keyboards.inline import callback_factories


class UserKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self, user_id: int, is_user_banned: bool,
                 callback_data: dict[str: str]):
        super().__init__()
        self.row(
            users_buttons.EditBalanceButton(user_id),
            users_buttons.TopUpBalanceButton(user_id),
            users_buttons.DeleteUserButton(user_id, **callback_data)
        )
        self.row(
            users_buttons.UnbanUserButton(user_id, **callback_data) if
            is_user_banned else users_buttons.BanUserButton(user_id,
                                                            **callback_data)
        )
        self.row(common_buttons.CloseButton())
        self.row(navigation_buttons.InlineBackButton(
            callback_factories.UserCallbackFactory().new(
                filter=callback_data['filter'], page=callback_data['page'],
                id='', action='', is_confirmed=''
            )))


class BalanceEditingReasonsKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self, user_id: int, balance: float):
        super().__init__()
        self.row(
            users_buttons.P2PDeliveryButton(user_id, balance),
            users_buttons.RefundedPaymentButton(user_id, balance),
            users_buttons.AdminMistakeButton(user_id, balance)
        )
        self.add(common_buttons.CloseButton())
        self.add(navigation_buttons.InlineBackButton(
            callback_factories.UserCallbackFactory().new(
                filter='', page='0', id=user_id, action='manage',
                is_confirmed=''
            )))


class BalanceRefillMethodsKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self, user_id: int, balance: float):
        super().__init__()
        self.row(
            users_buttons.CashAppPaymentMethod(user_id, balance),
            users_buttons.AnotherPaymentMethod(user_id, balance)
        )
        self.add(common_buttons.CloseButton())
        self.add(navigation_buttons.InlineBackButton(
            callback_factories.UserCallbackFactory().new(
                filter='', page='0', id=user_id, action='manage',
                is_confirmed=''
            )))
