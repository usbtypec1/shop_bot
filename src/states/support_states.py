from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import StatesGroup, State


class SupportTicketCreateStates(StatesGroup):
    confirm_rules = State()
    subject = State()
    issue = State()


class AnswerSupportRequest(state.StatesGroup):
    waiting_answer = state.State()
