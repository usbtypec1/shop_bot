from collections.abc import Iterable

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from categories.models import Category
from common.views import View
from products.callback_data import (
    UserProductDetailCallbackData,
    UserProductListCallbackData
)
from products.models import Product

__all__ = ('UserProductListView',)


class UserProductListView(View):
    text = '📝 Products Management'

    def __init__(
            self,
            *,
            categories: Iterable[Category] | None = None,
            products: Iterable[Product] | None = None,
    ):
        self.__categories: tuple[Category, ...] = (
            tuple() if categories is None else tuple(categories)
        )
        self.__products: tuple[Product, ...] = (
            tuple() if products is None else tuple(products)
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for category in self.__categories:

            markup.row(
                InlineKeyboardButton(
                    text=category.name_display,
                    callback_data=UserProductListCallbackData().new(
                        parent_id=category.id,
                    ),
                ),
            )

        for product in self.__products:

            markup.row(
                InlineKeyboardButton(
                    text=product.name,
                    callback_data=UserProductDetailCallbackData().new(
                        product_id=product.id,
                    ),
                ),
            )

        markup.row(
            InlineKeyboardButton(
                text='🚫 Close',
                callback_data='close',
            )
        )
        return markup
