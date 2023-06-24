from aiogram.dispatcher.filters import state

__all__ = (
    'UserSetSpecificBalanceStates',
    'UserBalanceTopUpStates',
    'UserDeleteStates',
    'SearchUsersStates',
    'EditBalanceStates',
)


class UserSetSpecificBalanceStates(state.StatesGroup):
    amount = state.State()
    reason = state.State()
    confirm = state.State()


class UserBalanceTopUpStates(state.StatesGroup):
    amount = state.State()
    payment_method = state.State()
    confirm = state.State()


class UserDeleteStates(state.StatesGroup):
    confirm = state.State()


class SearchUsersStates(state.StatesGroup):
    waiting_identifiers = state.State()


class EditBalanceStates(state.StatesGroup):
    waiting_balance = state.State()
