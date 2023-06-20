from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from common.views import View

__all__ = ('UserShoppingCartView',)


class UserShoppingCartView(View):

    def __init__(self, cart_products: Iterable):
        self.__cart_products = tuple(cart_products)

    def get_text(self) -> str:
        if not self.__cart_products:
            return '🛒 Your cart is empty'

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
