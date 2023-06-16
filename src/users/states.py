from aiogram.dispatcher.filters import state

__all__ = (
    'SearchUsersStates',
    'EditBalanceStates',
    'TopUpBalanceStates',
)


class SearchUsersStates(state.StatesGroup):
    waiting_identifiers = state.State()


class EditBalanceStates(state.StatesGroup):
    waiting_balance = state.State()


class TopUpBalanceStates(state.StatesGroup):
    waiting_balance = state.State()
