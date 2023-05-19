from collections.abc import Iterable

import aiogram.types

from keyboards.buttons import (
    category_management_buttons,
    common_buttons,
    navigation_buttons,
)
from keyboards.inline import callback_factories
from services.db_api import schemas


class CategoriesKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self, categories: Iterable[schemas.Category]):
        super().__init__(row_width=1)
        for category in categories:
            if category.icon is not None:
                text = f'{category.icon} {category.name}'
            else:
                text = category.name
            self.insert(
                category_management_buttons.CategoryButton(
                    category_id=category.id,
                    category_name=text,
                )
            )
        self.add(category_management_buttons.AddCategoriesButton())
        self.add(common_buttons.CloseButton())


class CategoryMenuKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self, category_id: int):
        super().__init__()
        self.row(category_management_buttons.AddSubcategoriesButton(category_id))
        self.row(category_management_buttons.EditSubcategoriesButton(category_id))
        # self.row(
        #     category_management_buttons.AddSubcategoriesButton(category_id),
        #     category_management_buttons.EditSubcategoriesButton(category_id)
        # )
        self.row(category_management_buttons.EditCategoryButton(category_id))
        self.row(category_management_buttons.DeleteSubcategoriesButton(category_id))
        self.row(category_management_buttons.DeleteCategoryButton(category_id))
        self.row(navigation_buttons.InlineBackButton(
            callback_query=callback_factories.CategoriesCallbackFactory().new(action='manage')),
            common_buttons.CloseButton()
        )

class SubcategoriesForRemovalKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self, subcategories: list[schemas.Subcategory], category_id: int):
        super().__init__(row_width=1)
        for subcategory in subcategories:
            self.add(
                category_management_buttons.SubcategoryForRemovalButton(
                    subcategory.name, subcategory.id, category_id=category_id
                )
            )
        self.row(
            navigation_buttons.InlineBackButton(
                callback_query=callback_factories.CategoryCallbackFactory().new(
                    action='manage', category_id=category_id, subcategory_id=''
                )
            ),
            common_buttons.CloseButton()
        )
