from aiogram.utils.callback_data import CallbackData

from products.models import PaymentMethod

__all__ = (
    'UserProductAddToCartCallbackData',
    'UserProductDetailCallbackData',
    'UserProductListCallbackData',
    'AdminProductDeleteCallbackData',
    'AdminProductUpdateCallbackData',
    'AdminProductPermittedGatewayChoiceCallbackData',
    'AdminProductCreateCallbackData',
    'AdminProductDetailCallbackData',
    'AdminProductListCallbackData',
    'ProductCallbackFactory',
    'ProductUnitCallbackFactory',
)


class ParseProductIdMixin:

    def parse(self, callback_data: str) -> dict:
        callback_data: dict[str, str] = super().parse(callback_data)
        return callback_data | {
            'product_id': int(callback_data['product_id']),
        }


class UserProductAddToCartCallbackData(ParseProductIdMixin, CallbackData):

    def __init__(self):
        super().__init__('user-product-add-to-cart', 'product_id')


class UserProductDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('user-product-detail', 'product_id')


class UserProductListCallbackData(CallbackData):

    def __init__(self):
        super().__init__('user-product-list', 'parent_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        if callback_data['parent_id'] == 'None':
            parent_id = None
        else:
            parent_id = int(callback_data['parent_id'])
        return {'parent_id': parent_id}


class AdminProductDeleteCallbackData(ParseProductIdMixin, CallbackData):

    def __init__(self):
        super().__init__('admin-product-delete', 'product_id')


class AdminProductUpdateCallbackData(ParseProductIdMixin, CallbackData):

    def __init__(self):
        super().__init__('admin-product-update', 'product_id', 'field')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return callback_data | {'field': callback_data['field']}


class AdminProductPermittedGatewayChoiceCallbackData(CallbackData):

    def __init__(self):
        super().__init__('permitted-gateway-choice', 'payment_method')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {
            'payment_method': PaymentMethod[callback_data['payment_method']],
        }


class AdminProductCreateCallbackData(CallbackData):

    def __init__(self):
        super().__init__('admin-product-create', 'category_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {'category_id': int(callback_data['category_id'])}


class AdminProductDetailCallbackData(ParseProductIdMixin, CallbackData):

    def __init__(self):
        super().__init__('admin-product-detail', 'product_id')


class AdminProductListCallbackData(CallbackData):

    def __init__(self):
        super().__init__('admin-product-list', 'parent_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        if callback_data['parent_id'] == 'None':
            parent_id = None
        else:
            parent_id = int(callback_data['parent_id'])
        return {'parent_id': parent_id}


class ProductCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__(
            'product',
            'category_id',
            'subcategory_id',
            'product_id',
            'action',
        )


class ProductUnitCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__(
            'product_unit',
            'category_id',
            'subcategory_id',
            'product_id',
            'id',
            'action',
        )
