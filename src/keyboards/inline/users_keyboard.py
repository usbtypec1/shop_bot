import aiogram.types

from keyboards.buttons import users_buttons, navigation_buttons, common_buttons
from keyboards.inline import callback_factories


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
