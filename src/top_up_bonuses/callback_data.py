from aiogram.utils.callback_data import CallbackData

__all__ = (
    'TopUpBonusDetailCallbackData',
    'TopUpBonusDeleteCallbackData',
    'TopUpBonusUpdateCallbackData',
)


class ParseTopUpBonusIdMixin:

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return callback_data | {
            'top_up_bonus_id': int(callback_data['top_up_bonus_id']),
        }


class TopUpBonusDetailCallbackData(ParseTopUpBonusIdMixin, CallbackData):

    def __init__(self):
        super().__init__('top-up-bonus-detail', 'top_up_bonus_id')


class TopUpBonusUpdateCallbackData(ParseTopUpBonusIdMixin, CallbackData):

    def __init__(self):
        super().__init__('top-up-bonus-update', 'top_up_bonus_id')


class TopUpBonusDeleteCallbackData(ParseTopUpBonusIdMixin, CallbackData):

    def __init__(self):
        super().__init__('top-up-bonus-delete', 'top_up_bonus_id')
