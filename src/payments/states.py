from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ('UserBalanceTopUpStates',)


class UserBalanceTopUpStates(StatesGroup):
    amount = State()
    payment_method = State()
