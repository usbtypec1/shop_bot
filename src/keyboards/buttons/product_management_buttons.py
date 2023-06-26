import aiogram.types

import products.callback_data


class CompleteProductAddingKeyboard(aiogram.types.KeyboardButton):
    def __init__(self):
        super().__init__('✅ Complete')


class EditProductTitleButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='📙 Change Product Title',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='edit_title'
            )
        )


class EditProductDescriptionButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='📝 Edit Description',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='edit_description'
            )
        )


class EditProductPictureButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='🖼 Change Product Image',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='edit_picture'
            )
        )


class EditProductPrice(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='💵 Change Price',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='edit_price'
            )
        )


class ProductUnitsManagementButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='📦 Manage Stock',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='units'
            )
        )


class AddProductUnitsButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='➕ Add More Stock',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='add_units'
            )
        )


class DeleteAllProductUnits(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='❌🗑 Remove All Stock',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='delete_units'
            )
        )


class DeleteProductButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_id: int, category_id: int,
                 subcategory_id: int = None):
        super().__init__(
            text='❌🗑 Remove This Product',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, action='delete'
            )
        )


class ProductUnitButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, content: str, category_id: int, product_id: int,
                 product_unit_id: int, subcategory_id: int = None):
        super().__init__(
            text=content,
            callback_data=products.callback_data.ProductUnitCallbackFactory().new(
                category_id=category_id, subcategory_id=subcategory_id or '',
                product_id=product_id, id=product_unit_id, action='manage',
            )
        )


class EditProductUnitButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_unit_id: int, category_id: int,
                 subcategory_id: int, product_id: int):
        super().__init__(
            text='📝 Edit',
            callback_data=products.callback_data.ProductUnitCallbackFactory().new(
                id=product_unit_id, category_id=category_id,
                subcategory_id=subcategory_id or '', product_id=product_id,
                action='edit'
            )
        )


class DeleteProductUnitButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, product_unit_id: int, category_id: int,
                 subcategory_id: int, product_id: int):
        super().__init__(
            text='🗑 Delete',
            callback_data=products.callback_data.ProductUnitCallbackFactory().new(
                id=product_unit_id, category_id=category_id,
                subcategory_id=subcategory_id or '', product_id=product_id,
                action='delete'
            )
        )


class BackToCategoriesButtons(aiogram.types.InlineKeyboardButton):
    def __init__(self):
        super().__init__(
            '⬅️ Back to category',
            callback_data=products.callback_data.ProductCallbackFactory().new(
                category_id='', subcategory_id='', product_id='',
                action='manage'
            )
        )
