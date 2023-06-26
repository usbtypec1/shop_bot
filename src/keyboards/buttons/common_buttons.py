import aiogram.utils.callback_data


class CloseButton(aiogram.types.InlineKeyboardButton):
    def __init__(self):
        super().__init__(text='🚫 Close', callback_data='close')
