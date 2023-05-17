import aiogram.types

from keyboards.buttons import shop_information_buttons


class FAQKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(shop_information_buttons.EditFAQButton())


class RulesKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(shop_information_buttons.EditRulesButton())


class GreetingsKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(shop_information_buttons.EditGreetingsButton())


class ComebackMessageKeyboard(aiogram.types.InlineKeyboardMarkup):
    def __init__(self):
        super().__init__()
        self.add(shop_information_buttons.EditComebackMessageButton())
