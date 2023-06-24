from aiogram.utils.callback_data import CallbackData

__all__ = (
    'UserDeleteCallbackData',
    'UserDetailCallbackData',
    'UserUpdateCallbackData',
    'UserBalanceTopUpCallbackData',
)


class ParseUserIdMixin:

    def parse(self, callback_data: str):
        callback_data = super().parse(callback_data)
        return callback_data | {'user_id': int(callback_data['user_id'])}


class UserUpdateCallbackData(ParseUserIdMixin, CallbackData):

    def __init__(self):
        super().__init__('user-update', 'user_id', 'field')


class UserDeleteCallbackData(ParseUserIdMixin, CallbackData):

    def __init__(self):
        super().__init__('user-delete', 'user_id')


class UserDetailCallbackData(ParseUserIdMixin, CallbackData):

    def __init__(self):
        super().__init__('user-detail', 'user_id')


class UserBalanceTopUpCallbackData(ParseUserIdMixin, CallbackData):

    def __init__(self):
        super().__init__('user-balance-top-up', 'user_id')
