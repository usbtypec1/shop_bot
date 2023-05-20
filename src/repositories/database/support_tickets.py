from sqlalchemy import select

import models
from repositories.database.base import BaseRepository
from services.db_api.schemas import SupportTicket


class SupportTicketRepository(BaseRepository):

    def get_by_id(self, support_ticket_id: int) -> models.SupportTicket:
        with self._session_factory() as session:
            support_ticket = session.get(SupportTicket, support_ticket_id)
        return models.SupportTicket(
            id=support_ticket.id,
            user_id=support_ticket.user_id,
            subject=support_ticket.subject,
            issue=support_ticket.issue,
            answer=support_ticket.answer,
            status=support_ticket.status,
        )

    def get_by_user_id(self, user_id: int) -> list[models.SupportTicket]:
        statement = (
            select(SupportTicket)
            .where(SupportTicket.user_id == user_id)
            .order_by(SupportTicket.created_at.desc())
            .limit(30)
        )
        with self._session_factory() as session:
            result = session.scalars(statement).all()
        return [
            models.SupportTicket(
                id=support_ticket.id,
                user_id=support_ticket.user_id,
                subject=support_ticket.subject,
                issue=support_ticket.issue,
                answer=support_ticket.answer,
                status=support_ticket.status,
            ) for support_ticket in result
        ]

    def create(
            self,
            *,
            user_id: int,
            subject: str,
            issue: str,
    ) -> models.SupportTicket:
        support_ticket = SupportTicket(
            user_id=user_id,
            subject=subject,
            issue=issue,
        )
        with self._session_factory() as session:
            with self._session_factory.begin():
                session.add(support_ticket)
                session.flush()
                session.refresh(support_ticket)
                session.commit()
        return models.SupportTicket(
            id=support_ticket.id,
            user_id=support_ticket.user_id,
            subject=support_ticket.subject,
            issue=support_ticket.issue,
            answer=support_ticket.answer,
            status=support_ticket.status,
        )
