from aiogram.dispatcher.filters.state import StatesGroup, State


class SupportTicketCreateStates(StatesGroup):
    confirm_rules = State()
    subject = State()
    issue = State()


class SupportTicketDeleteStatus(StatesGroup):
    confirm = State()


class AdminSupportTicketUpdateStates(StatesGroup):
    answer = State()
