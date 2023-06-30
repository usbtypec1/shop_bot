from collections.abc import Iterable
from functools import cached_property

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

import config
from categories.callback_data import (
    CategoryDeleteCallbackData,
    CategoryUpdateCallbackData,
    CategoryDetailCallbackData,
    SubcategoryListCallbackData,
    CategoryCreateCallbackData,
    UserCategoryDetailCallbackData,
)
from categories.models import Category
from common.views import View
from keyboards.buttons.common_buttons import CloseButton
from keyboards.buttons.navigation_buttons import InlineBackButton
from keyboards.inline.callback_factories import CategoriesCallbackFactory
from products.callback_data import UserProductDetailCallbackData
from products.models import Product

__all__ = (
    'CategoryDetailView',
    'CategoryListView',
    'CategoryAskDeleteConfirmationView',
    'UserCategoryListView',
    'UserCategoryDetailView',
)


class CategoryDisplayMixin:
    _is_subcategory: bool

    @property
    def category_singular_display(self) -> str:
        return 'subcategory' if self._is_subcategory else 'category'

    @property
    def category_plural_display(self) -> str:
        return 'subcategories' if self._is_subcategory else 'categories'


class CategoryListView(CategoryDisplayMixin, View):

    def __init__(
            self,
            categories: Iterable[Category],
            *,
            parent_id: int | None = None
    ):
        self.__categories = tuple(categories)
        self.__parent_id = parent_id
        self._is_subcategory = self.__parent_id is not None

    def get_text(self) -> str:
        return (
            f'📂 All available {self.category_plural_display}'
            if self.__categories
            else f'No available {self.category_plural_display}'
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
                    callback_data=CategoryDetailCallbackData().new(
                        category_id=category.id,
                    )
                ),
            )
        markup.insert(
            InlineKeyboardButton(
                f'📂 Add {self.category_singular_display.capitalize()}',
                callback_data=CategoryCreateCallbackData().new(
                    parent_id=str(self.__parent_id),
                ),
            ),
        )

        row = [
            InlineKeyboardButton(
                text='🚫 Close',
                callback_data='close',
            )
        ]
        if self._is_subcategory:
            row.insert(0, InlineKeyboardButton(
                text='⬅️ Back',
                callback_data=CategoryDetailCallbackData().new(
                    category_id=self.__parent_id,
                )
            ))
        markup.row(*row)

        return markup


class CategoryDetailView(View, CategoryDisplayMixin):

    def __init__(
            self,
            *,
            category: Category,
            subcategories: Iterable[Category],
    ):
        self.__category = category
        self.__subcategories = tuple(subcategories)
        self._is_subcategory: bool = self.__category.parent_id is not None

    def get_text(self) -> str:
        subcategories = [
            f"📍 {subcategory.name}" for subcategory in self.__subcategories
        ]
        subcategory_lines = '\n'.join(subcategories)
        is_shown_to_users = '❌' if self.__category.is_hidden else '✅'
        are_orders_prevented = '❌' if self.__category.can_be_seen else '✅'
        icon = self.__category.icon or 'notset'
        return (
            f'📁 {self.category_singular_display.capitalize()}:'
            f' {self.__category.name}\n'
            f'Icon: {icon}\n'
            f'Priority: {self.__category.priority}\n'
            f'Max Displayed Stocks: {self.__category.max_displayed_stock_count}\n'
            f'Shown to users: {is_shown_to_users}\n'
            f'Orders prevented: {are_orders_prevented}\n\n'
            '🗂 Available subcategories:\n'
            f'{subcategory_lines}\n\n'
            f'❗️ When deleting a {self.category_singular_display.capitalize()},'
            ' make sure to delete all products/subcategories in it'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        if not self._is_subcategory:
            markup.insert(
                InlineKeyboardButton(
                    text=f'✏️ Edit Subcategories',
                    callback_data=SubcategoryListCallbackData().new(
                        category_id=self.__category.id,
                    ),
                ),
            )

        buttons = (
            (f'📝 {self.category_singular_display.capitalize()} Title', 'name'),
            (f'📝 {self.category_singular_display.capitalize()} Icon', 'icon'),
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
            f'📝 Show {self.category_singular_display.capitalize()}'
            if self.__category.is_hidden
            else f'📝 Hide {self.category_singular_display.capitalize()}'
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
                callback_data=CategoryDeleteCallbackData().new(
                    category_id=self.__category.id,
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


class CategoryAskDeleteConfirmationView(CategoryDisplayMixin, View):

    def __init__(
            self,
            *,
            category_id: int,
            is_subcategory: bool,
            subcategories_count: int,
            products_count: int,

    ):
        self.__category_id = category_id
        self.__subcategories_count = subcategories_count
        self.__products_count = products_count
        self._is_subcategory = is_subcategory

    def get_text(self) -> str:
        text = (
            f'Are you sure you want to delete this'
            f' {self.category_singular_display} with'
        )
        if self._is_subcategory:
            text += f' {self.__subcategories_count} subcategories and'
        text += f' {self.__products_count} products'
        return text

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text='Yes',
                callback_data='category-delete-confirm',
            ),
            InlineKeyboardButton(
                text='No',
                callback_data=CategoryDetailCallbackData().new(
                    category_id=self.__category_id,
                ),
            ),
        )
        return markup


class UserCategoryListView(View):
    text = '📂 All available categories'

    def __init__(self, categories: Iterable[Category]):
        self.__categories = categories

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        for category in self.__categories:
            if category.is_hidden:
                continue

            text = (
                category.name if category.icon is None
                else f'{category.icon} {category.name}'
            )
            markup.insert(
                InlineKeyboardButton(
                    text=text,
                    callback_data=UserCategoryDetailCallbackData().new(
                        category_id=category.id,
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


class UserCategoryDetailView(View):

    def __init__(
            self,
            *,
            subcategories: Iterable[Category] | None = None,
            products: Iterable[Product] | None = None,
    ):
        self.__subcategories: tuple[Category, ...] = (
            tuple() if subcategories is None
            else tuple(subcategories)
        )
        self.__products: tuple[Product, ...] = (
            tuple() if products is None
            else tuple(products)
        )

    @cached_property
    def not_hidden_products(self) -> list[Product]:
        return [
            product for product in self.__products
            if not product.is_hidden
        ]

    @cached_property
    def not_hidden_subcategories(self) -> list[Category]:
        return [
            subcategory for subcategory in self.__subcategories
            if not subcategory.is_hidden
        ]

    @cached_property
    def products_and_subcategories_names(self) -> list[str]:
        not_hidden_product_names = [
            product.name for product in self.not_hidden_products
        ]
        not_hidden_subcategory_names = [
            subcategory.name for subcategory in self.not_hidden_subcategories
        ]
        return not_hidden_product_names + not_hidden_subcategory_names

    def get_text(self) -> str:
        if not self.not_hidden_products and not self.not_hidden_subcategories:
            return '😔 Oh, there is nothing here'

        names = self.products_and_subcategories_names
        # used to add extra text on specific categories, don't delete
        if any('Regular Products' in name for name in names):
            return config.CustomCategoryMessages().category1
        if any('Pre-Built Codes' in name for name in names):
            return config.CustomCategoryMessages().category2
        if any('Our Best Services' in name for name in names):
            return config.CustomCategoryMessages().category3

        return '🛒 All available products and subcategories'

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for subcategory in self.__subcategories:

            if subcategory.is_hidden:
                continue

            text = (
                subcategory.name if subcategory.icon is None
                else f'{subcategory.icon} {subcategory.name}'
            )

            markup.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=UserCategoryDetailCallbackData().new(
                        category_id=subcategory.id,
                    ),
                ),
            )

        for product in self.__products:

            if product.is_hidden:
                continue

            markup.row(
                InlineKeyboardButton(
                    text=product.name,
                    callback_data=UserProductDetailCallbackData().new(
                        product_id=product.id,
                    ),
                ),
            )

        markup.row(InlineKeyboardButton('🚫 Close', callback_data='close'))

        return markup
