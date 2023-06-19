from aiogram.utils.callback_data import CallbackData

__all__ = (
    'UserCategoryDetailCallbackData',
    'CategoryCreateCallbackData',
    'CategoryDeleteCallbackData',
    'CategoryDetailCallbackData',
    'CategoryUpdateCallbackData',
    'SubcategoryListCallbackData',
)


class UserCategoryDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('user-category-detail', 'category_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'category_id': int(callback_data['category_id'])}


class CategoryCreateCallbackData(CallbackData):

    def __init__(self):
        super().__init__('category-create', 'parent_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        parent_id = (
            int(callback_data['parent_id'])
            if callback_data['parent_id'].isdigit() else None
        )
        return {'parent_id': parent_id}


class CategoryDeleteCallbackData(CallbackData):

    def __init__(self):
        super().__init__('category-delete', 'category_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'category_id': int(callback_data['category_id'])}


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
