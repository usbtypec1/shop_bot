from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ('ShopInfoUpdateStates',)


class ShopInfoUpdateStates(StatesGroup):
    value = State()
