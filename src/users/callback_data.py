from aiogram.utils.callback_data import CallbackData

__all__ = (
    'UserDetailCallbackData',
)


class UserDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('user-detail', 'user_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {'user_id': int(callback_data['user_id'])}
