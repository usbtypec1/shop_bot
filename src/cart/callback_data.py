from aiogram.utils.callback_data import CallbackData

__all__ = (
    'CartProductDeleteCallbackData',
    'CartProductQuantityUpdateCallbackData',
)


class ParseCartProductIdMixin:

    def parse(self, callback_data: str) -> dict:
        callback_data: dict[str, str] = super().parse(callback_data)
        return callback_data | {
            'cart_product_id': int(callback_data['cart_product_id']),
        }


class CartProductDeleteCallbackData(ParseCartProductIdMixin, CallbackData):

    def __init__(self):
        super().__init__('cart-product-delete', 'cart_product_id')


class CartProductQuantityUpdateCallbackData(
    ParseCartProductIdMixin,
    CallbackData,
):

    def __init__(self):
        super().__init__(
            'cart-product-quantity-update',
            'cart_product_id',
            'action',
        )

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        action = callback_data['action']

        if action not in ('increment', 'decrement'):
            raise ValueError(f'Invalid action: {action}')

        return callback_data | {'action': action}
