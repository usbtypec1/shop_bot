import aiogram.types
from aiogram.types import KeyboardButton

from keyboards.buttons import payments_buttons, navigation_buttons
from payments.services import PaymentsAPIsRepository


class PaymentsKeyboard(aiogram.types.ReplyKeyboardMarkup):
    def __init__(self):
        super().__init__(row_width=3, resize_keyboard=True)
        buttons = {
            'qiwi': payments_buttons.ManageQIWIButton(),
            'yoomoney': payments_buttons.ManageYooMoneyButton(),
            'minerlock': payments_buttons.ManageMinerlockButton(),
            'coinpayments': payments_buttons.ManageCoinPaymentsButton(),
            'coinbase': payments_buttons.ManageCoinbaseButton(),
        }
        apis_repository = PaymentsAPIsRepository()
        for name, api in apis_repository.get_enabled_apis():
            self.add(buttons[name])
        self.row(KeyboardButton('Top Up Bonuses'))
        self.row(navigation_buttons.BackButton())
