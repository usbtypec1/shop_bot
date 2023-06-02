import datetime
from dataclasses import dataclass

from database.schemas import SupportTicketReplySource

__all__ = (
    'SupportTicketReplySource',
    'SupportTicketReply',
)


@dataclass(frozen=True, slots=True)
class SupportTicketReply:
    id: int
    text: str
    source: SupportTicketReplySource
    support_ticket_id: int
    created_at: datetime.datetime
