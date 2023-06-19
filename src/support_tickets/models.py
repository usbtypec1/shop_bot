import datetime
from dataclasses import dataclass

from database.schemas import SupportTicketReplySource, SupportTicketStatus

__all__ = (
    'SupportTicket',
    'SupportTicketStatus',
    'SupportTicketReplySource',
    'SupportTicketReply',

)


@dataclass(frozen=True, slots=True)
class SupportTicket:
    id: int
    user_id: int
    user_telegram_id: int
    subject: str
    issue: str
    answer: str | None
    status: SupportTicketStatus
    created_at: datetime.datetime

    @property
    def id_display(self) -> int:
        """
        Please use this property to display the ID in the UI.
        It is needed to enable visibility of a large number of requests.
        """
        return self.to_display_id(self.id)

    @staticmethod
    def to_display_id(value: int) -> int:
        """Convert internal ID to the display ID."""
        return value + 10015

    @staticmethod
    def to_internal_id(value: int) -> int:
        """
        Convert display ID to the ID which is stored in database.
        """
        return value - 10015


@dataclass(frozen=True, slots=True)
class SupportTicketReply:
    id: int
    text: str
    source: SupportTicketReplySource
    support_ticket_id: int
    created_at: datetime.datetime
