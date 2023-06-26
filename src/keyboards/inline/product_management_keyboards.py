from aiogram.types import InlineKeyboardMarkup

import products.callback_data
from database import schemas
from keyboards.buttons import (
    product_management_buttons,
    navigation_buttons,
    common_buttons,
)


class ProductKeyboard(InlineKeyboardMarkup):
    def __init__(self, category_id: int, product_id: int,
                 subcategory_id: int = None):
        super().__init__(row_width=1)
        self.add(
            product_management_buttons.EditProductTitleButton(product_id,
                                                              category_id,
                                                              subcategory_id),
            product_management_buttons.EditProductDescriptionButton(product_id,
                                                                    category_id,
                                                                    subcategory_id),
            product_management_buttons.EditProductPictureButton(product_id,
                                                                category_id,
                                                                subcategory_id),
            product_management_buttons.EditProductPrice(product_id, category_id,
                                                        subcategory_id),
            product_management_buttons.ProductUnitsManagementButton(product_id,
                                                                    category_id,
                                                                    subcategory_id)
        )
        self.row(
            product_management_buttons.AddProductUnitsButton(product_id,
                                                             category_id,
                                                             subcategory_id),
            product_management_buttons.DeleteAllProductUnits(product_id,
                                                             category_id,
                                                             subcategory_id))
        self.add(product_management_buttons.DeleteProductButton(product_id,
                                                                category_id,
                                                                subcategory_id))
        self.row(
            navigation_buttons.InlineBackButton(
                callback_query=products.callback_data.ProductCallbackFactory().new(
                    category_id=category_id,
                    subcategory_id=subcategory_id or '',
                    product_id='', action='manage'
                )
            ), product_management_buttons.BackToCategoriesButtons())
        self.add(common_buttons.CloseButton())


class ProductUnitsKeyboard(InlineKeyboardMarkup):
    def __init__(self, category_id: int, product_id: int,
                 product_units: list[schemas.ProductUnit],
                 subcategory_id: int = None):
        super().__init__()
        for unit in product_units:
            self.row(product_management_buttons.ProductUnitButton(
                unit.content, category_id, product_id, unit.id, subcategory_id
            ))
        self.row(navigation_buttons.InlineBackButton(
            callback_query=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='manage'
            )
        ))
        self.row(common_buttons.CloseButton())


class ProductUnitKeyboard(InlineKeyboardMarkup):
    def __init__(self, category_id: int, product_id: int, product_unit_id: int,
                 subcategory_id: int = None):
        super().__init__()
        self.row(
            product_management_buttons.EditProductUnitButton(
                product_unit_id, category_id, subcategory_id, product_id
            ),
            product_management_buttons.DeleteProductUnitButton(
                product_unit_id, category_id, subcategory_id, product_id
            )
        )
        self.row(navigation_buttons.InlineBackButton(
            callback_query=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id,
                subcategory_id=subcategory_id or '', product_id=product_id,
                action='units'
            )
        ))
