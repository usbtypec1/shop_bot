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
    user_telegram_id: int
    subject: str
    issue: str
    answer: str | None
    status: SupportTicketStatus

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
