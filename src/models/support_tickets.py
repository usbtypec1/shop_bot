from dataclasses import dataclass

from services.db_api.schemas import SupportTicketStatus

__all__ = (
    'SupportTicket',
    'SupportTicketStatus',
)


@dataclass(frozen=True, slots=True)
class SupportTicket:
    id: int
    user_id: int
    subject: str
    issue: str
    answer: str | None
    status: SupportTicketStatus
