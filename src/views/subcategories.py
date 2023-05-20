from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import models
from keyboards.inline.callback_factories import (
    SubcategoryDetailCallbackData,
    SubcategoryUpdateCallbackData,
    SubcategoryDeleteCallbackData,
)
from views.base import View

__all__ = (
    'SubcategoryListView',
    'SubcategoryDetailView',
    'SubcategoryAskDeleteConfirmationView',
)


class SubcategoryListView(View):

    def __init__(self, subcategories: Iterable[models.Subcategory]):
        self.__subcategories = tuple(subcategories)

    def get_text(self) -> str:
        return (
            'Choose subcategory to edit' if self.__subcategories
            else 'Oh, there is no any subcategory'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        for subcategory in self.__subcategories:
            text = (
                subcategory.name if subcategory.icon is None
                else f'{subcategory.icon} {subcategory.name}'
            )
            markup.insert(
                InlineKeyboardButton(
                    text=text,
                    callback_data=SubcategoryDetailCallbackData().new(
                        subcategory_id=subcategory.id,
                    ),
                ),
            )
        return markup


class SubcategoryDetailView(View):

    def __init__(self, subcategory: models.Subcategory):
        self.__subcategory = subcategory

    def get_text(self) -> str:
        is_shown_to_users = '❌' if self.__subcategory.is_hidden else '✅'
        are_orders_prevented = '❌' if self.__subcategory.can_be_seen else '✅'
        icon = self.__subcategory.icon or 'notset'
        return (
            f'📁 Category: {self.__subcategory.name}\n'
            f'Icon: {icon}\n'
            f'Priority: {self.__subcategory.priority}\n'
            'Max Displayed Stocks:'
            f' {self.__subcategory.max_displayed_stock_count}\n'
            f'Shown to users: {is_shown_to_users}\n'
            f'Orders prevented: {are_orders_prevented}\n\n'
            '❗️ When deleting a subcategory,'
            ' make sure to delete all products in it'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)
        buttons = (
            ('📝 Subcategory Title', 'name'),
            ('📝 Subcategory Icon', 'icon'),
            ('📝 Priority', 'priority'),
            ('📝 Max Displayed Stock', 'max-displayed-stock-count'),
        )
        for text, field_to_update in buttons:
            markup.insert(
                InlineKeyboardButton(
                    text=text,
                    callback_data=SubcategoryUpdateCallbackData().new(
                        subcategory_id=self.__subcategory.id,
                        field=field_to_update,
                    ),
                ),
            )
        hidden_status_button_text = (
             '📝 Show Category' if self.__subcategory.is_hidden
             else '📝 Hide Category'
        )
        markup.insert(
            InlineKeyboardButton(
                text=hidden_status_button_text,
                callback_data=SubcategoryUpdateCallbackData().new(
                    subcategory_id=self.__subcategory.id,
                    field='hidden-status',
                ),
            ),
        )

        can_be_seen_status_button_text = (
            '📝 Prevent Orders' if self.__subcategory.can_be_seen
            else '📝 Allow Orders'
        )
        markup.insert(
            InlineKeyboardButton(
                text=can_be_seen_status_button_text,
                callback_data=SubcategoryUpdateCallbackData().new(
                    subcategory_id=self.__subcategory.id,
                    field='can-be-seen-status',
                ),
            ),
        )
        markup.insert(
            InlineKeyboardButton(
                '❌🗑️ Delete Subcategory',
                callback_data=(
                    SubcategoryDeleteCallbackData().new(
                        subcategory_id=self.__subcategory.id,
                    )
                ),
            ),
        )
        return markup


class SubcategoryAskDeleteConfirmationView(View):
    text = '❗️ Are you sure you want to delete this subcategory?'

    def __init__(self, subcategory_id: int):
        self.__subcategory_id = subcategory_id

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text='Yes',
                callback_data='subcategory-delete-confirm',
            ),
            InlineKeyboardButton(
                text='No',
                callback_data=SubcategoryDetailCallbackData().new(
                    subcategory_id=self.__subcategory_id,
                ),
            ),
        )
        return markup
