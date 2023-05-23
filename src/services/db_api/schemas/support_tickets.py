import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    Enum,
)

from services.db_api.schemas.base import BaseModel

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

    user_id = Column(Integer, ForeignKey('user.telegram_id'), nullable=False)
    subject = Column(String(64), nullable=False)
    issue = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(
        Enum(SupportTicketStatus),
        default=SupportTicketStatus.OPEN,
        nullable=False,
    )


class SupportTicketReplySource(enum.Enum):
    USER = 'User'
    ADMIN = 'Admin'


class SupportTicketReply(BaseModel):
    __tablename__ = 'support_ticket_replies'

    support_ticket_id = Column(
        Integer,
        ForeignKey('support_tickets.id'),
        nullable=False,
    )
    source = Column(Enum(SupportTicketReplySource), nullable=False)
    text = Column(Text, nullable=False)
