from sqlalchemy import select

import models
from repositories.database.base import BaseRepository
from database.schemas import SupportTicketReply

__all__ = ('SupportTicketReplyRepository',)


class SupportTicketReplyRepository(BaseRepository):

    def create(
            self,
            *,
            support_ticket_id: int,
            source: models.SupportTicketReplySource,
            text: str,
    ):
        support_ticket_reply = SupportTicketReply(
            support_ticket_id=support_ticket_id,
            source=source,
            text=text
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(support_ticket_reply)
                session.flush()
                session.refresh(support_ticket_reply)
        return models.SupportTicketReply(
            id=support_ticket_reply.id,
            support_ticket_id=support_ticket_id,
            source=source,
            text=text,
            created_at=support_ticket_reply.created_at,
        )

    def get_by_support_ticket_id(
            self,
            support_ticket_id: int,
    ) -> list[models.SupportTicketReply]:
        statement = (
            select(SupportTicketReply)
            .where(SupportTicketReply.support_ticket_id == support_ticket_id)
            .order_by(SupportTicketReply.created_at.asc())
        )
        with self._session_factory() as session:
            result = session.scalars(statement).all()
        return [
            models.SupportTicketReply(
                id=support_ticket_reply.id,
                support_ticket_id=support_ticket_reply.support_ticket_id,
                source=support_ticket_reply.source,
                text=support_ticket_reply.text,
                created_at=support_ticket_reply.created_at,
            ) for support_ticket_reply in result
        ]
