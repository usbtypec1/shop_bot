from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from common.views import View

__all__ = ('TimeSensitiveDiscountMenuView',)


class TimeSensitiveDiscountMenuView(View):
    text = '% Time Sensitive Discounts'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('Create New Discount'),
                KeyboardButton('View Active Discounts'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )
