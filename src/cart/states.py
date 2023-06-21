from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ('UserShoppingCartAddToCartStates',)


class UserShoppingCartAddToCartStates(StatesGroup):
    quantity = State()
