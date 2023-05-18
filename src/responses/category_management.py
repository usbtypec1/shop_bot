from collections.abc import Iterable

from aiogram.types import CallbackQuery, Message

from keyboards.inline.category_management_keyboards import (
    SubcategoriesForRemovalKeyboard,
    CategoryMenuKeyboard,
    CategoriesKeyboard,
)
from responses.base import BaseResponse
from services.db_api import schemas


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


class AddCategoriesResponse(BaseResponse):
    def __init__(self, query: CallbackQuery):
        self.__query = query

    async def _send_response(self) -> Message:
        await self.__query.answer()
        return await self.__query.message.edit_text(
            '✏️ Enter the title\n'
            'One Category - in each row'
        )


class CategoryMenuResponse(BaseResponse):
    def __init__(
            self,
            update: CallbackQuery | Message,
            category_id: int,
            category_name: str,
            subcategories: list[schemas.Subcategory],
    ):
        self.__update = update
        self.__subcategories = subcategories
        self.__category_name = category_name
        self.__keyboard = CategoryMenuKeyboard(category_id=category_id)

    async def _send_response(self) -> Message:
        subcategories = [
            f"{i}. (ID: {subcategory.id}) {subcategory.name}"
            for i, subcategory in enumerate(self.__subcategories, start=1)
        ]
        subcategory_lines = '\n'.join(subcategories)
        message_text = (
            f'📁 Category:\n{self.__category_name}\n\n'
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


class SuccessRemovalCategoryResponse(BaseResponse):
    def __init__(self, query: CallbackQuery):
        self.__query = query

    async def _send_response(self) -> Message:
        await self.__query.answer()
        await self.__query.message.delete()
        return await self.__query.message.answer('✅ Category Removed')


class SuccessAddingCategoryResponse(BaseResponse):
    def __init__(self, message: Message, categories_quantity: int):
        self.__message = message
        self.__categories_quantity = categories_quantity

    async def _send_response(self) -> Message:
        return await self.__message.answer(
            text=f'✅ Total categories Added: {self.__categories_quantity}'
        )


class DeleteSubcategoriesResponse(BaseResponse):
    def __init__(
            self,
            update: CallbackQuery | Message,
            subcategories: list[schemas.Subcategory],
            category_id: int,
    ):
        self.__update = update
        self.__keyboard = SubcategoriesForRemovalKeyboard(
            subcategories=subcategories,
            category_id=category_id,
        )

    async def _send_response(self) -> Message:
        message_text = '📁 Select subcategory'
        match self.__update:
            case CallbackQuery():
                await self.__update.answer()
                return await self.__update.message.edit_text(
                    text=message_text,
                    reply_markup=self.__keyboard,
                )
            case Message():
                await self.__update.answer(
                    text=message_text,
                    reply_markup=self.__keyboard,
                )


class SuccessRemovalSubcategoryResponse(BaseResponse):
    def __init__(self, query: CallbackQuery):
        self.__query = query

    async def _send_response(self) -> Message:
        await self.__query.answer()
        return await self.__query.message.edit_text('✅ Category Removed')


class EditCategoryResponse(BaseResponse):
    def __init__(self, query: CallbackQuery, category_id: int):
        self.__query = query
        self.category_id = category_id

    async def _send_response(self) -> int:
        await self.__query.answer()
        await self.__query.message.answer(
            f'✏️ Enter the new name for Category {self.category_id}:'
        )
        return self.category_id


class EditSubcategoryResponse(BaseResponse):
    def __init__(self, query: CallbackQuery):
        self.__query = query

    async def _send_response(self) -> None:
        await self.__query.answer()
        await self.__query.message.answer(
            '🔢 Please enter the subcategory id that you want to edit'
            ' (after the (ID:) in the above list):'
        )
