import aiogram

from keyboards.inline import callback_factories


class P2PDeliveryButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int, balance: float):
        super().__init__(
            text='🤝 P2P Delivery',
            callback_data=callback_factories.EditUserBalanceCallbackFactory().new(
                user_id, balance=balance, reason='p2p_delivery',
                is_confirmed='yes'
            )
        )


class AdminMistakeButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int, balance: float):
        super().__init__(
            '🫤 Admin Mistake',
            callback_data=callback_factories.EditUserBalanceCallbackFactory().new(
                user_id, balance=balance, reason='admin_mistake',
                is_confirmed='yes'
            )
        )


class RefundedPaymentButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int, balance: float):
        super().__init__(
            '🔄 Refunded Payment',
            callback_data=callback_factories.EditUserBalanceCallbackFactory().new(
                user_id, balance=balance, reason='refunded_payment',
                is_confirmed='yes'
            )
        )
