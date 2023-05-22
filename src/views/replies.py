import models
from views.base import View

__all__ = ('SupportTicketReplyView',)


class SupportTicketReplyView(View):

    def __init__(self, support_ticket_reply: models.SupportTicketReply):
        self.__support_ticket_reply = support_ticket_reply

    def get_text(self) -> str:
        match self.__support_ticket_reply.source:
            case models.SupportTicketReplySource.USER():
                return f'From user: {self.__support_ticket_reply.text}'
            case models.SupportTicketReplySource.ADMIN():
                return f'From admin: {self.__support_ticket_reply.text}'
            case _:
                raise ValueError(
                    'Invalid support ticket reply source'
                    f' {self.__support_ticket_reply.source}'
                )
