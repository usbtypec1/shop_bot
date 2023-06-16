from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from categories.callback_data import (
    CategoryDeleteCallbackData,
    CategoryUpdateCallbackData,
    CategoryDetailCallbackData,
    SubcategoryListCallbackData,
    CategoryCreateCallbackData,

)
from categories.models import Category
from common.views import View
from keyboards.buttons.common_buttons import CloseButton
from keyboards.buttons.navigation_buttons import InlineBackButton
from keyboards.inline.callback_factories import (
    CategoriesCallbackFactory,
)

__all__ = (
    'CategoryDetailView',
    'CategoryListView',
    'CategoryAskDeleteConfirmationView',
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

        row = [CloseButton()]
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


class CategoryAskDeleteConfirmationView(View):
    text = '❗️ Are you sure you want to delete this category?'

    def __init__(self, category_id: int):
        self.__category_id = category_id

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
