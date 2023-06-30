from aiogram.dispatcher.filters.state import State, StatesGroup

__all__ = ('MailingStates',)


class MailingStates(StatesGroup):
    waiting_newsletter = State()
