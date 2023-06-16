from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from categories.models import Category
from common.views import View

__all__ = ('CategoryListView',)


class CategoryListView(View):
    text = '📝 Products Management'

    def __init__(self, categories: Iterable[Category]):
        self.__categories = tuple(categories)

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        for category in self.__categories:
            markup.row(
                InlineKeyboardButton(

                )
            )
        markup.row(
            InlineKeyboardButton(
                text='🚫 Close',
                callback_data='close',
            )
        )
        return markup
