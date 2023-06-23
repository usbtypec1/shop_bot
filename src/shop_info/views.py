from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from common.views import View
from keyboards.inline.callback_factories import ShopInfoUpdateCallbackData
from shop_info import models

__all__ = (
    'ShopInfoDetailView',
    'ShopInfoMenuView',
    'ShopManagementView',
)


class ShopInfoDetailView(View):

    def __init__(self, *, key: str, value: str):
        self.__key = key
        self.__value = value

    def get_text(self) -> str:
        return self.__value

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(
                text='📝 Edit',
                callback_data=ShopInfoUpdateCallbackData().new(
                    key=self.__key
                ),
            )
        )
        return markup


class ShopInfoMenuView(View):
    text = '🏪 Shop information'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(models.ShopInfo.FAQ.value),
                KeyboardButton(models.ShopInfo.RULES.value),
            ],
            [
                KeyboardButton(models.ShopInfo.GREETINGS.value),
                KeyboardButton(models.ShopInfo.RETURN.value),
                KeyboardButton(models.ShopInfo.SUPPORT_RULES.value),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class ShopManagementView(View):
    text = '🗂 Mng Categories & Prod'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('📝 Products Management'),
                KeyboardButton('📁 Categories Control'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )
