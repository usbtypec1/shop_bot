from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from common.views import View
from products.callback_data import UserProductAddToCartCallbackData
from products.models import Product

__all__ = ('UserProductDetailView',)


class UserProductDetailView(View):

    def __init__(self, product: Product):
        self.__product = product

    def get_text(self) -> str:
        lines = [
            f'📓 Name: {self.__product.name}',
            f'📋 Description:\n{self.__product.description}',
            f'💳 Price: ${self.__product.price:.2f}',
            f'📦 Available to purchase: {self.__product.quantity}'
            f' pc{"s" if self.__product.quantity > 1 else ""}',
        ]
        return '\n'.join(lines)

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='🛍️ Buy Now',
                        callback_data='buy-now',
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
