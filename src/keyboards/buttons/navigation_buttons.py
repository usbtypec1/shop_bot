from aiogram.types import InlineKeyboardButton


class InlineBackButton(InlineKeyboardButton):
    def __init__(self, callback_query: str):
        super().__init__(text='⬅️ Back', callback_data=callback_query)
