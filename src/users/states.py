from aiogram.dispatcher.filters import state

__all__ = (
    'UserDeleteStates',
    'SearchUsersStates',
    'EditBalanceStates',
    'TopUpBalanceStates',
)


class UserDeleteStates(state.StatesGroup):
    confirm = state.State()


class SearchUsersStates(state.StatesGroup):
    waiting_identifiers = state.State()


class EditBalanceStates(state.StatesGroup):
    waiting_balance = state.State()


class TopUpBalanceStates(state.StatesGroup):
    waiting_balance = state.State()
