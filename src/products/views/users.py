from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.services import render_money
from common.views import View
from products.callback_data import (
    UserProductAddToCartCallbackData,
    UserProductBuyCallbackData
)
from products.models import Product
from users.services import calculate_discounted_price

__all__ = ('UserProductDetailView',)


class UserProductDetailView(View):

    def __init__(self, *, product: Product, permanent_discount: int):
        self.__product = product
        self.__permanent_discount = permanent_discount

    def get_text(self) -> str:
        has_stocks = self.__product.quantity > 0
        has_single_stock = self.__product.quantity == 1
        is_stocks_displayed = self.__product.max_displayed_stock_count != 1

        if self.__permanent_discount == 0:
            price_to_display = f'${render_money(self.__product.price)}'
        else:
            discounted_price = calculate_discounted_price(
                original_price=self.__product.price,
                discount_percentage=self.__permanent_discount
            )
            price_to_display = (
                f'<s>${render_money(self.__product.price)}</s>'
                f' ${render_money(discounted_price)}'
            )

        if not is_stocks_displayed and has_stocks:
            stocks = 'In Stock'
        else:
            if self.__product.quantity > self.__product.max_displayed_stock_count:
                stocks = f'{self.__product.max_displayed_stock_count} pcs +'
            else:
                stocks = f'{self.__product.quantity} pc'
                if not has_single_stock:
                    stocks += 's'

        lines = [
            f'📓 Name: {self.__product.name}',
            f'📋 Description:\n{self.__product.description}',
            f'💳 Price: {price_to_display}',
            f'📦 Available to purchase: {stocks}'
        ]
        return '\n'.join(lines)

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='🛍️ Buy Now',
                        callback_data=UserProductBuyCallbackData().new(
                            product_id=self.__product.id,
                        ),
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='🛒 Add to Cart',
                        callback_data=UserProductAddToCartCallbackData().new(
                            product_id=self.__product.id,
                        )
                    ),
                ]
            ],
        )
