import asyncio
import contextlib
from decimal import Decimal

import coinbase_commerce
from coinbase_commerce import error
from coinbase_commerce.api_resources import charge

from payments.services.payments_apis import BasePaymentAPI


class CoinbaseAPI(BasePaymentAPI):
    def __init__(self, api_key: str):
        self.__client = coinbase_commerce.client.Client(api_key=api_key)

    async def create_charge(
            self,
            name: str,
            price: Decimal | str,
            description: str = None,
    ) -> charge.Charge:
        return await asyncio.to_thread(
            self.__client.charge.create,
            name=name,
            description=description,
            local_price={
                'amount': str(price),
                'currency': str('USD'),
            },
            pricing_type='fixed_price',
        )

    @staticmethod
    async def check_payment(payment: charge.Charge) -> bool:
        while not (status := payment['timeline'][-1]['status']) == 'COMPLETED':
            payment.refresh()
            if status in ('EXPIRED', 'CANCELED', 'UNRESOLVED'):
                if payment['timeline'][-1]['context'] == 'OVERPAID':
                    return True
                return False
            await asyncio.sleep(30)
        return True

    def check(self) -> bool:
        with contextlib.suppress(error.ResourceNotFoundError):
            try:
                self.__client.get()
            except error.AuthenticationError:
                return False
        return True
