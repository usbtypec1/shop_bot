from aiogram.utils.callback_data import CallbackData


class ProductCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__(
            'product',
            'category_id',
            'subcategory_id',
            'product_id',
            'action',
        )


class ProductUnitCallbackFactory(CallbackData):
    def __init__(self):
        super().__init__(
            'product_unit',
            'category_id',
            'subcategory_id',
            'product_id',
            'id',
            'action',
        )
