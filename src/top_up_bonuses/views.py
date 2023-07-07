from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from common.services import render_money
from common.views import View
from top_up_bonuses.callback_data import (
    TopUpBonusDetailCallbackData,
    TopUpBonusUpdateCallbackData,
    TopUpBonusDeleteCallbackData,
)
from top_up_bonuses.models import TopUpBonus

__all__ = (
    'TopUpBonusListView',
    'TopUpBonusMenuView',
    'TopUpBonusCreateUpdateAskForConfirmationView',
    'TopUpBonusCreateReceiptView',
    'TopUpBonusDeleteAskForConfirmationView',
    'TopUpBonusDetailView',
    'TopUpBonusUpdateReceiptView',
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
                KeyboardButton('View Active Top Up Bonuses'),
            ],
            [
                KeyboardButton('⬅️ Back'),
            ],
        ],
    )


class TopUpBonusCreateUpdateAskForConfirmationView(View):

    def __init__(
            self,
            *,
            minimum_amount: Decimal,
            bonus_percentage: int,
            starts_at: datetime | None,
            expires_at: datetime | None,
    ):
        self.__minimum_amount = minimum_amount
        self.__bonus_percentage = bonus_percentage
        self.__starts_at = starts_at
        self.__expires_at = expires_at

    def get_text(self) -> str:
        if self.__starts_at is None:
            starts_at = 'now'
        else:
            starts_at = f'{self.__starts_at:%m/%d/%Y %H:%M}'

        if self.__expires_at is None:
            expires_at = 'infinite'
        else:
            expires_at = f'{self.__expires_at:%m/%d/%Y %H:%M}'

        return (
            f'Are you sure you want to apply {self.__bonus_percentage}%'
            f' bonus to any amount above ${render_money(self.__minimum_amount)}'
            f' which begins in {starts_at}'
            f' and finishes in {expires_at}'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='top-up-bonus-create-update-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data='show-top-up-bonus-list',
                    ),
                ],
            ],
        )


class TopUpBonusCreateReceiptView(View):

    def __init__(
            self,
            *,
            minimum_amount: Decimal,
            bonus_percentage: int,
            starts_at: datetime | None,
            expires_at: datetime | None,
    ):
        self.__minimum_amount = minimum_amount
        self.__bonus_percentage = bonus_percentage
        self.__starts_at = starts_at
        self.__expires_at = expires_at

    def get_text(self) -> str:
        if self.__starts_at is None:
            starts_at = 'now'
        else:
            starts_at = f'{self.__starts_at:%m/%d/%Y %H:%M}'

        if self.__expires_at is None:
            expires_at = 'infinite'
        else:
            expires_at = f'{self.__expires_at:%m/%d/%Y %H:%M}'

        return (
            '<code>'
            'Minimum amount to activate this top up bonus:'
            f' ${render_money(self.__minimum_amount)}\n'
            f'Amount of bonus: {self.__bonus_percentage}%\n'
            f'Start Date: {starts_at}\n'
            f'Finish Date: {expires_at}\n'
            '</code>'
        )


class TopUpBonusDeleteAskForConfirmationView(View):

    def __init__(
            self,
            top_up_bonus: TopUpBonus,
    ):
        self.__top_up_bonus = top_up_bonus

    def get_text(self) -> str:
        return (
            'Are you sure you want to delete'
            f' {self.__top_up_bonus.bonus_percentage}% bonus on any amounts'
            f' above ${render_money(self.__top_up_bonus.min_amount_threshold)}?'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Yes',
                        callback_data='top-up-bonus-delete-confirm',
                    ),
                    InlineKeyboardButton(
                        text='No',
                        callback_data=TopUpBonusDetailCallbackData().new(
                            top_up_bonus_id=self.__top_up_bonus.id,
                        ),
                    ),
                ],
            ],
        )


class TopUpBonusDetailView(View):

    def __init__(self, top_up_bonus: TopUpBonus):
        self.__top_up_bonus = top_up_bonus

    def get_text(self) -> str:
        starts_at = f'{self.__top_up_bonus.starts_at:%m/%d/%Y %H:%M}'
        if self.__top_up_bonus.expires_at is None:
            expires_at = 'infinite'
        else:
            expires_at = f'{self.__top_up_bonus.expires_at:%m/%d/%Y %H:%M}'
        return (
            '<b>Top Up Bonus</b>\n'
            f'<b>Bonus:</b> {self.__top_up_bonus.bonus_percentage}\n'
            '<b>Min Amount:</b>'
            f' {render_money(self.__top_up_bonus.min_amount_threshold)}\n'
            f'<b>Start date</b>: {starts_at}\n'
            f'<b>End date</b>: {expires_at}'
        )

    def get_reply_markup(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='📝 Edit',
                        callback_data=TopUpBonusUpdateCallbackData().new(
                            top_up_bonus_id=self.__top_up_bonus.id,
                        ),
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text='🗑️ Delete',
                        callback_data=TopUpBonusDeleteCallbackData().new(
                            top_up_bonus_id=self.__top_up_bonus.id,
                        ),
                    ),
                ],
            ],
        )


class TopUpBonusUpdateReceiptView(View):

    def __init__(
            self,
            old_minimum_amount: Decimal,
            old_bonus_percentage: int,
            new_minimum_amount: Decimal,
            new_bonus_percentage: int,
            new_starts_at: datetime | None,
            new_expires_at: datetime | None,
    ):
        self.__old_minimum_amount = old_minimum_amount
        self.__old_bonus_percentage = old_bonus_percentage
        self.__new_minimum_amount = new_minimum_amount
        self.__new_bonus_percentage = new_bonus_percentage
        self.__new_starts_at = new_starts_at
        self.__new_expires_at = new_expires_at

    def get_text(self) -> str:
        if self.__new_starts_at is None:
            starts_at = 'now'
        else:
            starts_at = f'{self.__new_starts_at:%m/%d/%Y %H:%M}'

        if self.__new_expires_at is None:
            expires_at = 'infinite'
        else:
            expires_at = f'{self.__new_expires_at:%m/%d/%Y %H:%M}'

        return (
            '<code>'
            f'Previous Amount: ${render_money(self.__old_minimum_amount)}\n'
            f'Old Bonus: {self.__old_bonus_percentage}%\n'
            'New Minimum amount to activate this top up bonus:'
            f' ${render_money(self.__new_minimum_amount)}\n'
            f'New Amount of bonus: {self.__new_bonus_percentage}%\n'
            f'Start Date: {starts_at}\n'
            f'Finish Date: {expires_at}\n'
            '</code>'
        )
