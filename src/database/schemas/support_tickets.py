import enum

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.schemas.base import BaseModel

__all__ = (
    'SupportTicketStatus',
    'SupportTicket',
    'SupportTicketReplySource',
    'SupportTicketReply',
)


class SupportTicketStatus(enum.Enum):
    OPEN = 'Open'
    PENDING = 'Pending'
    ON_HOLD = 'On Hold'
    CLOSED = 'Closed'


class SupportTicket(BaseModel):
    __tablename__ = 'support_tickets'

    user_id: Mapped[int] = mapped_column(ForeignKey('user.telegram_id'))
    subject: Mapped[str] = mapped_column(String(64))
    issue: Mapped[str]
    answer: Mapped[str | None]
    status: Mapped[SupportTicketStatus] = mapped_column(
        default=SupportTicketStatus.OPEN,
    )

    replies = relationship(
        'SupportTicketReply',
        back_populates='ticket',
        cascade='all, delete',
    )


class SupportTicketReplySource(enum.Enum):
    USER = 'User'
    ADMIN = 'Admin'


class SupportTicketReply(BaseModel):
    __tablename__ = 'support_ticket_replies'

    ticket_id: Mapped[int] = mapped_column(
        ForeignKey('support_tickets.id', ondelete='CASCADE'),
    )
    source: Mapped[SupportTicketReplySource]
    text: Mapped[str]

    ticket = relationship(
        'SupportTicket',
        back_populates='replies',
        cascade='all, delete',
    )
