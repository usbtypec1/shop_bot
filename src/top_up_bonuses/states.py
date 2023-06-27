from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'TopUpBonusCreateStates',
    'TopUpBonusDeleteStates',
    'TopUpBonusUpdateStates',
)


class TopUpBonusCreateStates(StatesGroup):
    minimum_amount = State()
    bonus_percentage = State()
    starts_at = State()
    expires_at = State()
    confirm = State()


class TopUpBonusDeleteStates(StatesGroup):
    confirm = State()


class TopUpBonusUpdateStates(StatesGroup):
    minimum_amount = State()
    bonus_percentage = State()
    starts_at = State()
    expires_at = State()
    confirm = State()
