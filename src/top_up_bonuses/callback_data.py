from aiogram.utils.callback_data import CallbackData

__all__ = (
    'TopUpBonusDetailCallbackData',
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
