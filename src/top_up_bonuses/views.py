from collections.abc import Iterable

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from common.views import View
from top_up_bonuses.callback_data import TopUpBonusDetailCallbackData
from top_up_bonuses.models import TopUpBonus

__all__ = (
    'TopUpBonusListView',
    'TopUpBonusMenuView',
)


class TopUpBonusListView(View):

    def __init__(self, top_up_bonuses: Iterable[TopUpBonus]):
        self.__top_up_bonuses = tuple(top_up_bonuses)

    def get_text(self) -> str:
        return (
            'Top Up Bonuses' if self.__top_up_bonuses
            else 'No Top Up Bonuses available'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for top_up_bonus in self.__top_up_bonuses:
            starts_at = f'{top_up_bonus.starts_at:%m/%d/%Y %H:%M}'
            if top_up_bonus.expires_at is None:
                expires_at = 'infinite'
            else:
                expires_at = f'{top_up_bonus.expires_at:%m/%d/%Y %H:%M}'
            text = f'{starts_at} → {expires_at}'
            markup.row(
                InlineKeyboardButton(
                    text=text,
                    callback_data=TopUpBonusDetailCallbackData().new(
                        top_up_bonus_id=top_up_bonus.id,
                    ),
                ),
            )

        return markup


class TopUpBonusMenuView(View):
    text = 'Top Up Bonuses'
    reply_markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton('Create New Top Up Bonus'),
            ],
            [
                KeyboardButton('View Active Top Up Bonuses'),
            ],
        ],
    )
