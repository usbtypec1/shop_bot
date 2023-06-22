from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'UserShoppingCartAddToCartStates',
    'UserShoppingCartDeleteAllStates',
)


class UserShoppingCartAddToCartStates(StatesGroup):
    quantity = State()


class UserShoppingCartDeleteAllStates(StatesGroup):
    confirm = State()
