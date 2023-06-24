import aiogram

from keyboards.inline import callback_factories


class TopUpBalanceButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int):
        super().__init__(
            text='💸 Top Up Balance',
            callback_data=callback_factories.TopUpUserBalanceCallbackFactory().new(
                user_id=user_id, balance_delta='', payment_method='',
                is_confirmed=''
            )
        )


class EditBalanceButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int):
        super().__init__(
            text='⚖️ Edit Balance',
            callback_data=callback_factories.EditUserBalanceCallbackFactory().new(
                user_id=user_id, balance='', reason='', is_confirmed=''
            )
        )


class DeleteUserButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int, **callback_data):
        super().__init__(
            text='🫥 Delete User',
            callback_data=callback_factories.UserCallbackFactory().new(
                **callback_data)
        )


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


class CashAppPaymentMethod(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int, balance_delta: float):
        super().__init__(
            '💳 Cashapp',
            callback_data=callback_factories.TopUpUserBalanceCallbackFactory().new(
                user_id, balance_delta=balance_delta, payment_method='cashapp',
                is_confirmed='yes'
            )
        )


class AnotherPaymentMethod(aiogram.types.InlineKeyboardButton):
    def __init__(self, user_id: int, balance_delta: float):
        super().__init__(
            '💎 Other',
            callback_data=callback_factories.TopUpUserBalanceCallbackFactory().new(
                user_id, balance_delta=balance_delta, payment_method='other',
                is_confirmed='yes'
            )
        )
