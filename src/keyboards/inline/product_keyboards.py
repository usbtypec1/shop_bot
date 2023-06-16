from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup

import products.callback_data
from categories.models import Category
from database import schemas
from keyboards.buttons import (
    product_buttons,
    common_buttons,
    navigation_buttons,
)


class CategoriesKeyboard(InlineKeyboardMarkup):
    def __init__(self, categories: Iterable[Category]):
        super().__init__(row_width=1)
        for category in categories:
            if category.is_hidden:
                continue
            self.row(product_buttons.CategoryButton(category.id, category.name))
        self.add(common_buttons.CloseButton())


class CategoryItemsKeyboard(InlineKeyboardMarkup):
    def __init__(
            self,
            *,
            subcategories: Iterable[Category],
            products: list[tuple[int, str, str]],
            category_id: int,
    ):
        super().__init__(row_width=1)

        for subcategory in subcategories:
            if subcategory.is_hidden:
                continue
            self.row(product_buttons.SubcategoryButton(
                subcategory_id=subcategory.id,
                subcategory_name=subcategory.name,
                category_id=category_id,
            )
        )

        for item_id, item_name, _ in products:
            self.row(product_buttons.ProductButton(item_id, item_name, category_id))
        self.add(navigation_buttons.InlineBackButton(
            callback_query=products.callback_data.ProductCallbackFactory().new(
                action='buy', category_id='', subcategory_id='', product_id=''
            ))
        )
        self.add(common_buttons.CloseButton())


class SubcategoryProductsKeyboard(InlineKeyboardMarkup):
    def __init__(self, products: list[schemas.Product], category_id: int, subcategory_id: int):
        super().__init__(row_width=1)
        for product in products:
            # product_name = f'{product.name} | $ {product.price} | {product.quantity} pc(s)'
            # product_name = f'{product.name} | ${product.price:.2f}'
            formatted_price = f"${product.price:.0f}" if product.price.is_integer() else f"${product.price:.2f}"
            product_name = f'{product.name} | {formatted_price}'

            # product_name = f'{product.name} | ${product.price:.2f}' if product.price % 1 else f'{product.name} | ${product.price:.0f}.'
            self.add(product_buttons.ProductButton(product.id, product_name, category_id, subcategory_id))
        self.add(navigation_buttons.InlineBackButton(
            callback_query=products.callback_data.ProductCallbackFactory().new(
                action='buy', category_id=category_id, subcategory_id='', product_id=''
            ))
        )
        self.add(common_buttons.CloseButton())


class ProductKeyboard(InlineKeyboardMarkup):
    def __init__(self, product_id: int, available_quantity: int, category_id: int,
                 subcategory_id: int = None, is_available=True):
        super().__init__(row_width=1)
        if is_available:
            self.add(product_buttons.BuyProductButton(product_id, available_quantity))
        self.row(
            navigation_buttons.InlineBackButton(
                products.callback_data.ProductCallbackFactory().new(
                    action='buy', category_id=category_id, subcategory_id=subcategory_id or '', product_id='')
            ),
            product_buttons.BackToCategoriesButton()
        )
        self.add(common_buttons.CloseButton())


# class ProductQuantityKeyboard(InlineKeyboardMarkup):
#     def __init__(self, product_id: int, available_quantity: int):
#         super().__init__(row_width=5)
#         self.add(
#             *[product_buttons.ProductQuantityButton(product_id, available_quantity, i)
#               for i in range(1, available_quantity + 1)]
#         )
#         self.row(product_buttons.AnotherQuantityButton(product_id, available_quantity))

# class ProductQuantityKeyboard(InlineKeyboardMarkup):
#     def __init__(self, product_id: int, available_quantity: int, max_buttons: int = 5):
#         super().__init__(row_width=5)

#         button_quantity = min(available_quantity, max_buttons)
#         self.add(
#             *[product_buttons.ProductQuantityButton(product_id, available_quantity, i)
#               for i in range(1, button_quantity + 1)]
#         )
#         self.row(product_buttons.AnotherQuantityButton(product_id, available_quantity))

class ProductQuantityKeyboard(InlineKeyboardMarkup):
    def __init__(self, product_id: int, available_quantity: int, max_buttons: int = 5):
        super().__init__(row_width=5)

        base_buttons = min(available_quantity, max_buttons)
        self.add(
            *[product_buttons.ProductQuantityButton(product_id, available_quantity, i)
              for i in range(1, base_buttons + 1)]
        )

        additional_buttons = []
        for i in range(base_buttons + 1, available_quantity + 1):
            if i % 10 == 0:
                additional_buttons.append(product_buttons.ProductQuantityButton(product_id, available_quantity, i))

        self.add(*additional_buttons)
        self.row(product_buttons.AnotherQuantityButton(product_id, available_quantity))
