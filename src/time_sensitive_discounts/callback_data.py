from aiogram.utils.callback_data import CallbackData

__all__ = (
    'TimeSensitiveDiscountDetailCallbackData',
    'TimeSensitiveDiscountUpdateCallbackData',
    'TimeSensitiveDiscountDeleteCallbackData',
)


class ParseTimeSensitiveDiscountIdMixin:

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return callback_data | {
            'time_sensitive_discount_id': (
                int(callback_data['time_sensitive_discount_id']),
            ),
        }


class TimeSensitiveDiscountDetailCallbackData(
    ParseTimeSensitiveDiscountIdMixin,
    CallbackData,
):

    def __init__(self):
        super().__init__(
            'time-sensitive-discount-detail',
            'time_sensitive_discount_id',
        )


class TimeSensitiveDiscountUpdateCallbackData(
    ParseTimeSensitiveDiscountIdMixin,
    CallbackData,
):

    def __init__(self):
        super().__init__(
            'time-sensitive-discount-update',
            'time_sensitive_discount_id',
        )


class TimeSensitiveDiscountDeleteCallbackData(
    ParseTimeSensitiveDiscountIdMixin,
    CallbackData,
):

    def __init__(self):
        super().__init__(
            'time-sensitive-discount-delete',
            'time_sensitive_discount_id',
        )
