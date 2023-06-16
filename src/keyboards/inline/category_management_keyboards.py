from collections.abc import Iterable

import aiogram.types
from aiogram.types import InlineKeyboardButton

from keyboards.buttons import (
    category_management_buttons,
    common_buttons,
    navigation_buttons,
)
from keyboards.inline import callback_factories
from categories.callback_data import (
    SubcategoryListCallbackData,
    CategoryUpdateCallbackData
)
from database import schemas


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
    def __init__(self, category_id: int, has_subcategories: bool):
        super().__init__()
        self.row(category_management_buttons.AddSubcategoriesButton(category_id))

        if has_subcategories:
            self.row(
                InlineKeyboardButton(
                    text='✏️ Edit Subcategories',
                    callback_data=SubcategoryListCallbackData().new(
                        category_id=category_id,
                    ),
                ),
            )

        buttons = (
            ('📝 Category Title', 'name'),
            ('📝 Category Icon', 'icon'),
            ('📝 Priority', 'priority'),
            ('📝 Max Displayed Stock', 'max-displayed-stock-count'),
            ('📝 Hide Category', 'hidden-status'),
            ('📝 Prevent Orders', 'can-be-seen-status'),
        )

        for text, field_to_update in buttons:
            self.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=CategoryUpdateCallbackData().new(
                        category_id=category_id,
                        field=field_to_update,
                    ),
                ),
            )

        self.row(category_management_buttons.DeleteCategoryButton(category_id))
        self.row(navigation_buttons.InlineBackButton(
            callback_query=callback_factories.CategoriesCallbackFactory().new(action='manage')),
            common_buttons.CloseButton()
        )
