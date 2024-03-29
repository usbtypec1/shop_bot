from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'SupportTicketDeleteStatus',
    'SupportTicketSearchStates',
    'SupportTicketCreateStates',
    'SupportTicketReplyCreateStates',
    'AdminSupportTicketUpdateStates',
)


class SupportTicketSearchStates(StatesGroup):
    user_id = State()
    date_range = State()
    status = State()


class SupportTicketCreateStates(StatesGroup):
    confirm_rules = State()
    subject = State()
    issue = State()


class SupportTicketDeleteStatus(StatesGroup):
    confirm = State()


class AdminSupportTicketUpdateStates(StatesGroup):
    answer = State()


class SupportTicketReplyCreateStates(SupportTicketDeleteStatus):
    text = State()
