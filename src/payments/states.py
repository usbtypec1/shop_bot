from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = ('TopUpBalance',)


class TopUpBalance(StatesGroup):
    waiting_for_amount = State()
