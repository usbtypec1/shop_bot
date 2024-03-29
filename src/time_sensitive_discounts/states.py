from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'TimeSensitiveDiscountCreateStates',
    'TimeSensitiveDiscountDeleteStates',
    'TimeSensitiveDiscountUpdateStates',
)


class TimeSensitiveDiscountCreateStates(StatesGroup):
    starts_at = State()
    expires_at = State()
    code = State()
    discount_value = State()
    confirm = State()


class TimeSensitiveDiscountUpdateStates(StatesGroup):
    starts_at = State()
    expires_at = State()
    code = State()
    discount_value = State()
    confirm = State()


class TimeSensitiveDiscountDeleteStates(StatesGroup):
    confirm = State()
