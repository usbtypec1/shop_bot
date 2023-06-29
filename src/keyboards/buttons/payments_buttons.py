import aiogram.utils.callback_data


class QiwiButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_data: dict[str: str],
                 callback_factory: aiogram.utils.callback_data.CallbackData):
        callback_data['payment_method'] = 'qiwi'
        super().__init__('🥝 QIWI',
                         callback_data=callback_factory.new(**callback_data))


class YooMoneyButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_data: dict[str: str],
                 callback_factory: aiogram.utils.callback_data.CallbackData):
        callback_data['payment_method'] = 'yoomoney'
        super().__init__('💵 YooMoney',
                         callback_data=callback_factory.new(**callback_data))


class MinerlockButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_data: dict[str: str],
                 callback_factory: aiogram.utils.callback_data.CallbackData):
        callback_data['payment_method'] = 'minerlock'
        super().__init__('📩 Minerlock',
                         callback_data=callback_factory.new(**callback_data))


class CoinPaymentsButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_data: dict[str: str],
                 callback_factory: aiogram.utils.callback_data.CallbackData):
        callback_data['payment_method'] = 'coinpayments'
        super().__init__('🔗 CoinPayments',
                         callback_data=callback_factory.new(**callback_data))


class CoinBaseButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_data: dict[str: str],
                 callback_factory: aiogram.utils.callback_data.CallbackData):
        callback_data['payment_method'] = 'coinbase'
        super().__init__('🌐 Coinbase',
                         callback_data=callback_factory.new(**callback_data))


class CryptoPaymentButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_data: dict[str: str], payment_method: str,
                 callback_factory: aiogram.utils.callback_data.CallbackData):
        callback_data['payment_method'] = payment_method
        super().__init__('💱 Cryptocurrency',
                         callback_data=callback_factory.new(**callback_data))


class BalanceButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, callback_data: dict[str: str],
                 callback_factory: aiogram.utils.callback_data.CallbackData):
        callback_data['payment_method'] = 'balance'
        super().__init__('💲 Balance',
                         callback_data=callback_factory.new(**callback_data))


class PayWithCoinbaseButton(aiogram.types.InlineKeyboardButton):
    def __init__(self, payment_url: str):
        super().__init__('🧾 Pay', url=payment_url)
