from collections.abc import Iterable
from typing import Protocol

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from cart.models import CartProduct
from common.views import View

__all__ = (
    'UserShoppingCartView',
    'ProductQuantityOutOfRangeWarningView',
)


class HasOptionalMinAndMaxOrderQuantity(Protocol):
    min_order_quantity: int | None
    max_order_quantity: int | None


class UserShoppingCartView(View):

    def __init__(self, cart_products: Iterable[CartProduct]):
        self.__cart_products = tuple(cart_products)

    def get_text(self) -> str:
        if not self.__cart_products:
            return '🛒 Your cart is empty'

        cart_products_total_count = sum(
            cart_product.quantity for cart_product in self.__cart_products
        )
        cart_products_total_cost = sum(
            cart_product.total_cost for cart_product in self.__cart_products
        )

        return (
            f'Total items: {cart_products_total_count}'
            f' / Total Amount: ${cart_products_total_cost:.2f}'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        if not self.__cart_products:
            markup.row(
                InlineKeyboardButton(
                    text='Shop Now',
                    callback_data='show-top-level-categories-list',
                ),
            )
            return markup

        for cart_product in self.__cart_products:
            markup.row(
                InlineKeyboardButton(
                    text=cart_product.product.name,
                    callback_data='dev',
                ),
                InlineKeyboardButton(
                    text='+',
                    callback_data='dev',
                ),
                InlineKeyboardButton(
                    text=f'{cart_product.quantity}',
                    callback_data='dev',
                ),
                InlineKeyboardButton(
                    text='-',
                    callback_data='dev',
                ),
                InlineKeyboardButton(
                    text='❌',
                    callback_data='dev',
                ),
            )

        markup.row(
            InlineKeyboardButton(
                text='🛒 Continue Shopping',
                callback_data='show-top-level-categories-list',
            ),
        )
        markup.row(
            InlineKeyboardButton(
                text='🛍️ Buy Now',
                callback_data='dev',
            ),
        )
        markup.row(
            InlineKeyboardButton(
                text='🗑️ Empty Cart',
                callback_data='dev',
            )
        )

        return markup


class ProductQuantityOutOfRangeWarningView(View):

    def __init__(self, product: HasOptionalMinAndMaxOrderQuantity):
        self.__product = product

    def get_text(self) -> str:
        has_min_order_quantity = self.__product.min_order_quantity is not None
        has_max_order_quantity = self.__product.max_order_quantity is not None

        if has_min_order_quantity and has_max_order_quantity:
            return (
                'You can\'t order less than'
                f' {self.__product.min_order_quantity}'
                f' or more than {self.__product.max_order_quantity}'
            )
        if has_min_order_quantity:
            return (
                'You can\'t order less than'
                f' {self.__product.min_order_quantity}'
            )
        if has_max_order_quantity:
            return (
                'You can\'t order more than'
                f' {self.__product.max_order_quantity}'
            )
        raise ValueError(
            'Neither `min_order_quantity` nor `max_order_quantity`'
            ' has been specified for this product'
        )
