from aiogram.utils.callback_data import CallbackData


class BuyProductCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('buy_product', 'product_id', 'available_quantity',
                         'quantity', 'payment_method')


class TopUpBalanceCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('top_up_balance', 'amount', 'payment_method')


class CategoriesCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('categories', 'action')


class MailingCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('mailing', 'markup')


class ShopInfoUpdateCallbackData(CallbackData):
    def __init__(self):
        super().__init__(
            'shop-info-update',
            'key',
        )


class UserCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('users', 'filter', 'page', 'id', 'action',
                         'is_confirmed')


class SupportCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('support', 'is_open', 'user_id', 'request_id',
                         'action')


class PaymentSystemCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('payment_system', 'system', 'action')
