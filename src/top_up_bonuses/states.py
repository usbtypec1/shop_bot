from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ('TopUpBonusCreateStates',)


class TopUpBonusCreateStates(StatesGroup):
    minimum_amount = State()
    bonus_percentage = State()
    starts_at = State()
    expires_at = State()
