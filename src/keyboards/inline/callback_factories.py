from aiogram.utils.callback_data import CallbackData


class BuyProductCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('buy_product', 'product_id', 'available_quantity',
                         'quantity', 'payment_method')


class CategoriesCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('categories', 'action')


class UserCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('users', 'filter', 'page', 'id', 'action',
                         'is_confirmed')
