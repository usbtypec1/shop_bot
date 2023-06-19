import aiogram.types
from aiogram.types import KeyboardButton

from keyboards.buttons import navigation_buttons


class ShopManagementKeyboard(aiogram.types.ReplyKeyboardMarkup):
    def __init__(self):
        super().__init__(resize_keyboard=True)
        self.row(
            KeyboardButton('📝 Products Management'),
            KeyboardButton('📁 Categories Control'),
        )
        self.row(navigation_buttons.BackButton())
