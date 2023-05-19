from aiogram.utils.callback_data import CallbackData


class SubcategoryDeleteCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-delete', 'subcategory_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'subcategory_id': int(callback_data['subcategory_id'])}


class SubcategoryUpdateCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-update', 'subcategory_id', 'field')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {
            'subcategory_id': int(callback_data['subcategory_id']),
            'field': callback_data['field'],
        }


class SubcategoryDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-detail', 'subcategory_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'subcategory_id': int(callback_data['subcategory_id'])}


class SubcategoryListCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-list', 'category_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'category_id': int(callback_data['category_id'])}


class CategoryUpdateCallbackData(CallbackData):

    def __init__(self):
        super().__init__('category-update', 'category_id', 'field')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {
            'category_id': int(callback_data['category_id']),
            'field': callback_data['field'],
        }


class ProductCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('product', 'category_id', 'subcategory_id',
                         'product_id', 'action')


class ProductUnitCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__(
            'product_unit', 'category_id', 'subcategory_id',
            'product_id', 'id', 'action'
        )


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


class CategoryCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('category', 'category_id', 'subcategory_id', 'action')


class MailingCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('mailing', 'markup')


class ShopInformationFactory(CallbackData):
    def __init__(self):
        super().__init__('shop_information', 'object', 'action')


class UserCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('users', 'filter', 'page', 'id', 'action',
                         'is_confirmed')


class EditUserBalanceCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('edit_balance', 'user_id', 'balance', 'reason',
                         'is_confirmed')


class TopUpUserBalanceCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('top_up_balance', 'user_id', 'balance_delta',
                         'payment_method', 'is_confirmed')


class SupportCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('support', 'is_open', 'user_id', 'request_id',
                         'action')


class CreateSupportCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('create_support', 'subject_id')


class PaymentSystemCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__('payment_system', 'system', 'action')
