from aiogram.utils.callback_data import CallbackData

__all__ = (
    'CategoryDeleteCallbackData',
    'CategoryDetailCallbackData',
    'CategoryUpdateCallbackData',
    'SubcategoryListCallbackData',
    'SubcategoryUpdateCallbackData',
    'SubcategoryDeleteCallbackData',
    'SubcategoryDetailCallbackData',
)


class CategoryDeleteCallbackData(CallbackData):

    def __init__(self):
        super().__init__('category-delete', 'category_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'category_id': int(callback_data['category_id'])}


class SubcategoryDeleteCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-delete', 'subcategory_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'subcategory_id': int(callback_data['subcategory_id'])}


class SubcategoryUpdateCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-update', 'subcategory_id', 'field')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {
            'subcategory_id': int(callback_data['subcategory_id']),
            'field': callback_data['field'],
        }


class SubcategoryDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-detail', 'subcategory_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'subcategory_id': int(callback_data['subcategory_id'])}


class CategoryDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('category-detail', 'category_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'category_id': int(callback_data['category_id'])}


class SubcategoryListCallbackData(CallbackData):

    def __init__(self):
        super().__init__('subcategory-list', 'category_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'category_id': int(callback_data['category_id'])}


class CategoryUpdateCallbackData(CallbackData):

    def __init__(self):
        super().__init__('category-update', 'category_id', 'field')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {
            'category_id': int(callback_data['category_id']),
            'field': callback_data['field'],
        }
