from aiogram.dispatcher.filters import state

__all__ = (
    'UserBalanceTopUpStates',
    'UserDeleteStates',
    'SearchUsersStates',
    'EditBalanceStates',
    'TopUpBalanceStates',
)


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


class TopUpBalanceStates(state.StatesGroup):
    waiting_balance = state.State()
