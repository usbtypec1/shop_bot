from aiogram.dispatcher.filters.state import StatesGroup, State


class ShopInfoUpdateStates(StatesGroup):
    value = State()
