from aiogram.utils.callback_data import CallbackData

__all__ = (
    'PaymentSystemCredentialsUpdateCallbackData',
    'PaymentSystemCredentialsStatusCallbackData',
)


class PaymentSystemCredentialsUpdateCallbackData(CallbackData):

    def __init__(self):
        super().__init__('payment-system-credentials-update', 'system')


class PaymentSystemCredentialsStatusCallbackData(CallbackData):

    def __init__(self):
        super().__init__('payment-system-credentials-update', 'system')
