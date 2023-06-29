from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'UserBalanceTopUpStates',
    'CoinbaseCredentialsUpdateStates',
)


class CoinbaseCredentialsUpdateStates(StatesGroup):
    api_key = State()


class UserBalanceTopUpStates(StatesGroup):
    amount = State()
    payment_method = State()
