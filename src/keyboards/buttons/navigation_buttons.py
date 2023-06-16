import aiogram


class BackButton(aiogram.types.KeyboardButton):
    def __init__(self):
        super().__init__('⬅️ Back')


class InlineBackButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_query: str):
        super().__init__(text='⬅️ Back', callback_data=callback_query)
