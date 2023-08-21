import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.schemas.base import BaseModel


class ReplacementRequestStatus(enum.Enum):
    OPEN = 'Open'
    PENDING = 'Pending'
    ON_HOLD = 'On Hold'
    REJECTED = 'Rejected'
    REPLACED = 'Replaced'
    MORE_INFO = 'More Info'


class ReplacementRequest(BaseModel):
    __tablename__ = 'replacement_requests'

    product_id: Mapped[int]
    issue: Mapped[str]
    photo: Mapped[str | None]
    answer: Mapped[str | None]
    status: Mapped[ReplacementRequestStatus] = mapped_column(
        default=ReplacementRequestStatus.OPEN,
    )

    product = relationship('Product', back_populates='replacement_requests')




class ReplacementRequestReply(BaseModel):
    __tablename__ = 'replacement_request_replies'

    request_id: Mapped[int] = mapped_column(
        ForeignKey('replacement_requests.id', ondelete='CASCADE'),
    )
    source: Mapped[ReplySource]
    text: Mapped[str]

    ticket = relationship(
        'SupportTicket',
        back_populates='replies',
        cascade='all, delete',
    )
