from collections.abc import Iterable

from aiogram.types import CallbackQuery, Message

from categories.models import Category
from database import schemas
from keyboards.inline.category_management_keyboards import (
    CategoryMenuKeyboard,
    CategoriesKeyboard,
)
from responses.base import BaseResponse


class CategoriesResponse(BaseResponse):
    def __init__(
            self,
            update: Message | CallbackQuery,
            categories: Iterable[schemas.Category],
    ):
        self.__update = update
        self.__keyboard = CategoriesKeyboard(categories=categories)

    async def _send_response(self) -> Message:
        message_text = '📂 All available categories'
        match self.__update:
            case Message():
                return await self.__update.answer(
                    text=message_text,
                    reply_markup=self.__keyboard,
                )
            case CallbackQuery():
                await self.__update.answer()
                return await self.__update.message.edit_text(
                    message_text, reply_markup=self.__keyboard
                )


class CategoryMenuResponse(BaseResponse):
    def __init__(
            self,
            update: CallbackQuery | Message,
            category: Category,
            subcategories: list[Category],
    ):
        self.__update = update
        self.__subcategories = subcategories
        self.__category = category
        self.__keyboard = CategoryMenuKeyboard(
            category_id=category.id,
            has_subcategories=bool(self.__subcategories),
        )

    async def _send_response(self) -> Message:
        subcategories = [
            f"{i}. (ID: {subcategory.id}) {subcategory.name}"
            for i, subcategory in enumerate(self.__subcategories, start=1)
        ]
        subcategory_lines = '\n'.join(subcategories)
        is_shown_to_users = '❌' if self.__category.is_hidden else '✅'
        are_orders_prevented = '❌' if self.__category.can_be_seen else '✅'
        icon = self.__category.icon or 'notset'
        message_text = (
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
        match self.__update:
            case CallbackQuery():
                await self.__update.answer()
                return await self.__update.message.edit_text(
                    text=message_text,
                    reply_markup=self.__keyboard,
                )
            case Message():
                return await self.__update.answer(
                    text=message_text,
                    reply_markup=self.__keyboard,
                )
