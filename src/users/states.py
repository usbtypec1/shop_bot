from aiogram.dispatcher.filters.state import State, StatesGroup

__all__ = (
    'UserUpdateStates',
    'UserSetSpecificBalanceStates',
    'UserBalanceTopUpStates',
    'UserDeleteStates',
    'SearchUsersStates',
)


class UserUpdateStates(StatesGroup):
    max_cart_cost = State()


class UserSetSpecificBalanceStates(StatesGroup):
    amount = State()
    reason = State()
    confirm = State()


class UserBalanceTopUpStates(StatesGroup):
    amount = State()
    payment_method = State()
    confirm = State()


class UserDeleteStates(StatesGroup):
    confirm = State()


class SearchUsersStates(StatesGroup):
    waiting_identifiers = State()
