from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'CategoryCreateStates',
    'CategoryUpdateStates',
    'CategoryDeleteStates',
)


class CategoryCreateStates(StatesGroup):
    name = State()
    icon = State()
    priority = State()
    max_displayed_stocks_count = State()
    is_hidden = State()
    can_be_seen = State()


class CategoryUpdateStates(StatesGroup):
    name = State()
    icon = State()
    priority = State()
    max_displayed_stocks_count = State()


class CategoryDeleteStates(StatesGroup):
    confirm = State()
