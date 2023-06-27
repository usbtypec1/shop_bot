from aiogram.utils.callback_data import CallbackData

from support.models import SupportTicketStatus, SupportTicketReplySource


class SupportTicketReplyListCallbackData(CallbackData):

    def __init__(self):
        super().__init__(
            'support-ticket-reply-list',
            'support_ticket_id',
        )


class SupportTicketReplyCreateCallbackData(CallbackData):

    def __init__(self):
        super().__init__(
            'support-ticket-reply-create',
            'support_ticket_id',
            'source',
        )

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {
            'support_ticket_id': int(callback_data['support_ticket_id']),
            'source': SupportTicketReplySource[callback_data['source']],
        }


class SupportTicketAnswerUpdateCallbackData(CallbackData):

    def __init__(self):
        super().__init__(
            'support-ticket-answer-update',
            'support_ticket_id',
        )

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {'support_ticket_id': int(callback_data['support_ticket_id'])}


class SupportTicketDeleteCallbackData(CallbackData):

    def __init__(self):
        super().__init__(
            'support-ticket-delete',
            'support_ticket_id',
        )

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {'support_ticket_id': int(callback_data['support_ticket_id'])}


class SupportTicketStatusUpdateCallbackData(CallbackData):

    def __init__(self):
        super().__init__(
            'support-ticket-status-update',
            'support_ticket_id',
            'status',
        )

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {
            'support_ticket_id': int(callback_data['support_ticket_id']),
            'status': SupportTicketStatus[callback_data['status']],
        }


class SupportTicketStatusListCallbackData(CallbackData):

    def __init__(self):
        super().__init__('support-ticket-status-list', 'support_ticket_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data)
        return {'support_ticket_id': int(callback_data['support_ticket_id'])}


class AdminSupportTicketDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('admin-support-ticket', 'support_ticket_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'support_ticket_id': int(callback_data['support_ticket_id'])}


class SupportTicketDetailCallbackData(CallbackData):

    def __init__(self):
        super().__init__('support-ticket', 'support_ticket_id')

    def parse(self, callback_data: str) -> dict:
        callback_data = super().parse(callback_data=callback_data)
        return {'support_ticket_id': int(callback_data['support_ticket_id'])}
