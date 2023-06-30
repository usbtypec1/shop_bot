from collections.abc import Generator
from decimal import Decimal, InvalidOperation
from typing import TypeAlias

from pydantic import BaseSettings

import config
from payments.exceptions import BalanceAmountValidatorError
from payments.services.payments_apis import (
    BasePaymentAPI,
    MinerlockAPI,
    CoinPaymentsAPI,
    CoinbaseAPI,
)

API: TypeAlias = tuple[str, BasePaymentAPI]


class PaymentsAPIsRepository:
    def __init__(self, crypto_payments: str = None):
        self.__settings_repository = PaymentsAPIsSettingsRepository()
        self.__apis: dict[str: BasePaymentAPI] = {
            'minerlock': MinerlockAPI(
                self.__settings_repository.get('minerlock').api_id,
                self.__settings_repository.get('minerlock').api_key
            ),
            'coinpayments': CoinPaymentsAPI(
                self.__settings_repository.get('coinpayments').public_key,
                self.__settings_repository.get('coinpayments').secret_key
            ),
            'coinbase': CoinbaseAPI(
                self.__settings_repository.get('coinbase').api_key),
        }
        if crypto_payments is not None:
            self.__apis['crypto_payments'] = self.__apis[crypto_payments]
            self.__apis.pop('minerlock')
            self.__apis.pop('coinbase')
            self.__apis.pop('coinpayments')
            self.__settings_repository.add(
                'crypto_payments',
                self.__settings_repository.get(
                    crypto_payments
                )
            )

    def get_enabled_apis(self) -> Generator[API, None, None]:
        for name, api in self.__apis.items():
            if self.__settings_repository.get(name).is_enabled:
                yield name, api

    def get_valid_apis(self) -> Generator[API, None, None]:
        for name, api in self.__apis.items():
            settings = self.__settings_repository.get(name)
            if settings is not None and settings.is_enabled and api.check():
                yield name, api


class PaymentsAPIsSettingsRepository:
    def __init__(self):
        self.__settings = {
            'qiwi': config.QIWISettings(),
            'yoomoney': config.YooMoneySettings(),
            'minerlock': config.MinerlockSettings(),
            'coinpayments': config.CoinpaymentsSettings(),
            'coinbase': config.CoinbaseSettings()
        }

    def get(self, name: str):
        return self.__settings.get(name)

    def add(self, name: str, settings: BaseSettings):
        self.__settings[name] = settings


def parse_balance_amount(text) -> Decimal:
    """
    Validates and converts a text representation
     of an amount to a Decimal value.

    Args:
        text (str): The text representation of the amount.

    Returns:
        Decimal: The converted Decimal value.

    Raises:
        InvalidOperation: If the text cannot be converted to a Decimal value.
    """
    try:
        return Decimal(text.replace(',', '.'))
    except InvalidOperation:
        raise BalanceAmountValidatorError
