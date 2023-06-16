from aiogram.dispatcher.filters.state import State, StatesGroup

__all__ = ('MailingStates', 'ChangeCoinbaseData')


class MailingStates(StatesGroup):
    waiting_newsletter = State()


class ChangeCoinbaseData(StatesGroup):
    waiting_api_key = State()
