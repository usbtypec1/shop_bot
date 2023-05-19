from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import models
from keyboards.buttons.common_buttons import CloseButton
from keyboards.buttons.navigation_buttons import InlineBackButton
from keyboards.inline.callback_factories import (
    CategoryCallbackFactory,
    SubcategoryListCallbackData,
    CategoryUpdateCallbackData,
    CategoriesCallbackFactory,
)
from views.base import View

__all__ = (
    'CategoryDetailView',
    'CategoryListView',
)


class CategoryListView(View):

    def __init__(self, categories: Iterable[models.Category]):
        self.__categories = tuple(categories)

    def get_text(self) -> str:
        return (
            '📂 All available categories'
            if self.__categories
            else 'No available categories'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        for category in self.__categories:
            text = (
                category.name if category.icon is None
                else f'{category.icon} {category.name}'
            )
            markup.insert(
                InlineKeyboardButton(
                    text=text,
                    callback_data=CategoryCallbackFactory().new(
                        action='manage',
                        category_id=category.id,
                        subcategory_id='',
                    )
                ),
            )
        markup.insert(
            InlineKeyboardButton(
                '📂 Add Category',
                callback_data=CategoriesCallbackFactory().new(
                    action='add',
                ),
            ),
        )
        markup.insert(CloseButton())
        return markup


class CategoryDetailView(View):

    def __init__(
            self,
            *,
            category: models.Category,
            subcategories: Iterable[models.Subcategory],
    ):
        self.__category = category
        self.__subcategories = tuple(subcategories)

    def get_text(self) -> str:
        subcategories = [
            f"📍 {subcategory.name}" for subcategory in self.__subcategories
        ]
        subcategory_lines = '\n'.join(subcategories)
        is_shown_to_users = '❌' if self.__category.is_hidden else '✅'
        are_orders_prevented = '❌' if self.__category.can_be_seen else '✅'
        icon = self.__category.icon or 'notset'
        return (
            f'📁 Category: {self.__category.name}\n'
            f'Icon: {icon}\n'
            f'Priority: {self.__category.priority}\n'
            f'Max Displayed Stocks: {self.__category.max_displayed_stock_count}\n'
            f'Shown to users: {is_shown_to_users}\n'
            f'Orders prevented: {are_orders_prevented}\n\n'
            '🗂 Available subcategories:\n'
            f'{subcategory_lines}\n\n'
            '❗️ When deleting a category/subcategory,'
            ' make sure to delete all products/subcategories in it'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        markup.insert(
            InlineKeyboardButton(
                text='📂 Add subcategories',
                callback_data=CategoryCallbackFactory().new(
                    action='add_subcategories',
                    category_id=self.__category.id,
                    subcategory_id='',
                )
            ),
        )

        if self.__subcategories:
            markup.insert(
                InlineKeyboardButton(
                    text='✏️ Edit Subcategories',
                    callback_data=SubcategoryListCallbackData().new(
                        category_id=self.__category.id,
                    ),
                ),
            )

        buttons = (
            ('📝 Category Title', 'name'),
            ('📝 Category Icon', 'icon'),
            ('📝 Priority', 'priority'),
            ('📝 Max Displayed Stock', 'max-displayed-stock-count'),
        )

        for text, field_to_update in buttons:
            markup.insert(
                InlineKeyboardButton(
                    text=text,
                    callback_data=CategoryUpdateCallbackData().new(
                        category_id=self.__category.id,
                        field=field_to_update,
                    ),
                ),
            )
        hidden_status_button_text = (
             '📝 Show Category' if self.__category.is_hidden
             else '📝 Hide Category'
        )
        markup.insert(
            InlineKeyboardButton(
                text=hidden_status_button_text,
                callback_data=CategoryUpdateCallbackData().new(
                    category_id=self.__category.id,
                    field='hidden-status',
                ),
            ),
        )

        can_be_seen_status_button_text = (
            '📝 Prevent Orders' if self.__category.can_be_seen
            else '📝 Allow Orders'
        )
        markup.insert(
            InlineKeyboardButton(
                text=can_be_seen_status_button_text,
                callback_data=CategoryUpdateCallbackData().new(
                    category_id=self.__category.id,
                    field='can-be-seen-status',
                ),
            ),
        )
        markup.insert(
            InlineKeyboardButton(
                text='❌🗑 Delete Category',
                callback_data=CategoryCallbackFactory().new(
                    action='delete',
                    category_id=self.__category.id,
                    subcategory_id='',
                ),
            ),
        )
        markup.row(
            InlineBackButton(
                callback_query=CategoriesCallbackFactory().new(
                    action='manage',
                )
            ),
            CloseButton(),
        )
        return markup
