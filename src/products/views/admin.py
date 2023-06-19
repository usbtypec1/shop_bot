from collections.abc import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from categories.models import Category
from common.views import View
from products.callback_data import (
    AdminProductListCallbackData,
    AdminProductDetailCallbackData,
    AdminProductCreateCallbackData,
    AdminProductUpdateCallbackData,
    AdminProductDeleteCallbackData,
    AdminProductPermittedGatewayChoiceCallbackData,
)
from products.models import Product, PaymentMethod

__all__ = (
    'AdminProductPermittedGatewaysView',
    'AdminProductListView',
    'AdminProductDetailView',
    'AdminAskForProductMediaView',
    'AdminProductDeleteView',
)


class AdminProductDeleteView(View):
    text = '❗️ Are you sure you want to delete this product?'

    def __init__(self, product_id: int):
        self.__product_id = product_id

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='❌ Delete',
                        callback_data='delete-confirm'
                    ),
                    InlineKeyboardButton(
                        text='⬅️ Back',
                        callback_data=AdminProductDetailCallbackData().new(
                            product_id=self.__product_id,
                        ),
                    ),
                ],
            ],
        )


class AdminAskForProductMediaView(View):
    text = (
        '📷/📹/🎥 You can include multiple images and videos'
        ' for each product, but only one GIF file.'
        '\n\nPlease note that if you upload more than one photo or video,'
        ' the product buttons will not be inlined'
        ' (they won\'t be attached to the group of images or videos).'
        ' Also ensure that your videos are in MP4 format.'
        '\n\nIf you want to add multiple images and/or videos,'
        ' kindly press the "Complete" button once you have'
        ' finished sending all of them.'
        '\n\nYou must send media files one by one ❗️'
    )
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Complete',
                    callback_data='complete-product-picture-uploading',
                ),
            ],
        ]
    )


class AdminProductListView(View):
    text = '📝 Products Management'

    def __init__(
            self,
            *,
            parent_id: int | None = None,
            categories: Iterable[Category] | None = None,
            products: Iterable[Product] | None = None,
    ):
        self.__parent_id = parent_id
        self.__is_subcategories = self.__parent_id is not None
        self.__categories: tuple[Category, ...] = (
            tuple() if categories is None else tuple(categories)
        )
        self.__products: tuple[Product, ...] = (
            tuple() if products is None else tuple(products)
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for category in self.__categories:

            markup.row(
                InlineKeyboardButton(
                    text=category.name_display,
                    callback_data=AdminProductListCallbackData().new(
                        parent_id=category.id,
                    ),
                ),
            )

        for product in self.__products:

            markup.row(
                InlineKeyboardButton(
                    text=product.name,
                    callback_data=AdminProductDetailCallbackData().new(
                        product_id=product.id,
                    ),
                ),
            )

        if self.__is_subcategories:
            markup.row(
                InlineKeyboardButton(
                    text='➕ Add Product',
                    callback_data=AdminProductCreateCallbackData().new(
                        category_id=self.__parent_id
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


class AdminProductDetailView(View):

    def __init__(self, product: Product):
        self.__product = product

    def get_text(self) -> str:
        duplicated_entries_status_text = (
            '✅ Duplicated entries allowed'
            if self.__product.is_duplicated_stock_entries_allowed
            else '❌ Duplicated entries prevented'
        )
        hidden_status_text = (
            '❌ Hidden' if self.__product.is_hidden
            else '✅ Shown to users'
        )
        can_be_purchased_status = (
            '✅ Purchases allowed' if self.__product.can_be_purchased
            else '❌ Purchases prevented'
        )
        lines = [
            f'📓 Name: {self.__product.name}',
            f'📋 Description:\n{self.__product.description}',
            f'💳 Price: ${self.__product.price:.2f}',
            f'📦 Available to purchase: {self.__product.quantity}'
            f' pc{"s" if self.__product.quantity > 1 else ""}',
            f'📦 Min Order Quantity: {self.__product.min_order_quantity}',
            f'📦 Max Order Quantity: {self.__product.max_order_quantity}',
            f'📦Max Displayed Stock: {self.__product.max_displayed_stock_count}',
            '⌛️ Max Replacement Time:'
            f' {self.__product.max_replacement_time_in_minutes} min.',
            duplicated_entries_status_text,
            hidden_status_text,
            can_be_purchased_status,
        ]
        if self.__product.permitted_gateways:
            lines.append('📲 Permitted Gateways:')
            lines += [
                f'▫️ {payment_method.value}'
                for payment_method in self.__product.permitted_gateways
            ]
        return '\n'.join(lines)

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        buttons = (
            ('📝 Product Name', 'name'),
            ('📝 Product Description', 'description'),
            ('📝 Price', 'price'),
            ('📝 Min Order Qty.', 'min-order-quantity'),
            ('📝 Max Order Qty.', 'max-order-quantity'),
            ('📝 Max Displayed Stock', 'max-displayed-stock'),
            ('📝 Max Replacement Time', 'max-replacement-time'),
            ('📝 Permitted Gateways', 'permitted-gateways'),
            ('🖼️ Media', 'media')
        )

        markup = InlineKeyboardMarkup()

        for text, field_to_update in buttons:
            markup.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=AdminProductUpdateCallbackData().new(
                        product_id=self.__product.id,
                        field=field_to_update,
                    )
                )
            )

        duplicated_entries_status_button_text = (
            '❌ Prevent Duplicated Entries'
            if self.__product.is_duplicated_stock_entries_allowed
            else '✅ Allow Duplicated Entries'
        )

        markup.row(
            InlineKeyboardButton(
                text=duplicated_entries_status_button_text,
                callback_data=AdminProductUpdateCallbackData().new(
                    product_id=self.__product.id,
                    field='duplicated-entries-status',
                ),
            ),
        )

        hidden_status_button_text = (
            '✅ Show Product'
            if self.__product.is_hidden
            else '❌ Hide Product'
        )

        markup.row(
            InlineKeyboardButton(
                text=hidden_status_button_text,
                callback_data=AdminProductUpdateCallbackData().new(
                    product_id=self.__product.id,
                    field='hidden-status',
                ),
            ),
        )

        can_be_purchased_status_button_text = (
            '❌ Prevent Purchasing'
            if self.__product.can_be_purchased
            else '✅ Allow Purchasing'
        )

        markup.row(
            InlineKeyboardButton(
                text=can_be_purchased_status_button_text,
                callback_data=AdminProductUpdateCallbackData().new(
                    product_id=self.__product.id,
                    field='can-be-purchased-status',
                ),
            ),
        )

        markup.row(
            InlineKeyboardButton(
                text='❌🗑️ Delete',
                callback_data=AdminProductDeleteCallbackData().new(
                    product_id=self.__product.id,
                ),
            ),
        )
        markup.row(
            InlineKeyboardButton(
                text='⬅️ Back',
                callback_data=AdminProductListCallbackData().new(
                    parent_id=self.__product.category_id,
                ),
            ),
        )

        return markup


class AdminProductPermittedGatewaysView(View):
    text = 'Permitted Gateways'

    def __init__(
            self,
            *,
            payment_method: type[PaymentMethod],
            chosen_payment_methods: Iterable[PaymentMethod] | None = None,
    ):
        self.__chosen_payment_methods = (
            set() if chosen_payment_methods is None
            else set(chosen_payment_methods)
        )
        self.__payment_method = payment_method

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        for payment_method in self.__payment_method:

            text = (
                f'✅ {payment_method.value}'
                if payment_method in self.__chosen_payment_methods
                else f'❌ {payment_method.value}'
            )
            markup.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=(
                        AdminProductPermittedGatewayChoiceCallbackData().new(
                            payment_method=payment_method.name,
                        )
                    ),
                ),
            )

        markup.row(
            InlineKeyboardButton(
                text='✅ Finish',
                callback_data='permitted-gateways-choose-finish',
            )
        )

        return markup
