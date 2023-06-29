from aiogram.utils.callback_data import CallbackData


class ShopInfoUpdateCallbackData(CallbackData):
    def __init__(self):
        super().__init__(
            'shop-info-update',
            'key',
        )
