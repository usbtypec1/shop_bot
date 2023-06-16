from aiogram.types import InlineKeyboardMarkup

import products.callback_data
from categories.models import Category
from database import schemas
from keyboards.buttons import (
    product_management_buttons,
    navigation_buttons,
    common_buttons,
)


class CategoriesKeyboard(InlineKeyboardMarkup):
    def __init__(self, categories: list[Category]):
        super().__init__(row_width=1)
        for category in categories:
            self.add(product_management_buttons.CategoryButton(category.name,
                                                               category.id))
        self.add(common_buttons.CloseButton())


class CategoryItemsKeyboard(InlineKeyboardMarkup):
    def __init__(self, items: list[tuple[int, str, str]], category_id: int):
        super().__init__(row_width=1)
        for item_id, item_name, item_type in items:
            if item_type == 'subcategory':
                self.add(
                    product_management_buttons.SubcategoryButton(category_id,
                                                                 item_id,
                                                                 item_name))
            elif item_type == 'product':
                self.add(product_management_buttons.ProductButton(category_id,
                                                                  item_id,
                                                                  item_name))
        self.add(product_management_buttons.AddProductButton(category_id))
        self.add(navigation_buttons.InlineBackButton(
            callback_query=products.callback_data.ProductCallbackFactory().new(
                category_id='', subcategory_id='', product_id='',
                action='manage'
            )
        ))
        self.add(common_buttons.CloseButton())


class SubcategoryProductsKeyboard(InlineKeyboardMarkup):
    def __init__(self, products: list[schemas.Product], subcategory_id: int,
                 category_id: int):
        super().__init__(row_width=1)
        # for product in products:
        #     self.add(product_management_buttons.ProductButton(
        #         category_id, product.id, f'{product.name} | ${product.price} | {product.quantity} pc(s)')
        #     )
        for product in products:
            formatted_price = f"${product.price:.0f}" if product.price.is_integer() else f"${product.price:.2f}"
            # product_name = f'{product.name} | {formatted_price} | {product.quantity} pc(s)'
            product_name = f'{product.name} | {formatted_price} | {product.quantity} pc{"s" if product.quantity > 1 else ""}'
            self.add(product_management_buttons.ProductButton(category_id,
                                                              product.id,
                                                              product_name))

        self.add(product_management_buttons.AddProductButton(category_id,
                                                             subcategory_id=subcategory_id))
        self.add(navigation_buttons.InlineBackButton(
            callback_query=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id='', product_id='',
                action='manage'))
        )
        self.add(common_buttons.CloseButton())


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
