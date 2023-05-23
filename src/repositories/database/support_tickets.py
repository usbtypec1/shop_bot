from sqlalchemy import select, delete, update

import models
from repositories.database.base import BaseRepository
from services.db_api.schemas import SupportTicket, SupportTicketStatus, User


class SupportTicketRepository(BaseRepository):

    def get_by_id(self, support_ticket_id: int) -> models.SupportTicket:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.id == support_ticket_id)
        )
        with self._session_factory() as session:
            result = session.execute(statement).first()
        support_ticket, telegram_id = result
        return models.SupportTicket(
            id=support_ticket.id,
            user_id=support_ticket.user_id,
            user_telegram_id=telegram_id,
            subject=support_ticket.subject,
            issue=support_ticket.issue,
            answer=support_ticket.answer,
            status=support_ticket.status,
            created_at=support_ticket.created_at,
        )

    def get_by_user_telegram_id(
            self,
            user_telegram_id: int,
    ) -> list[models.SupportTicket]:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(User.telegram_id == user_telegram_id)
            .order_by(SupportTicket.created_at.desc())
            .limit(30)
        )
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [
            models.SupportTicket(
                id=support_ticket.id,
                user_id=support_ticket.user_id,
                user_telegram_id=telegram_id,
                subject=support_ticket.subject,
                issue=support_ticket.issue,
                answer=support_ticket.answer,
                status=support_ticket.status,
                created_at=support_ticket.created_at,
            ) for support_ticket, telegram_id in result
        ]

    def create(
            self,
            *,
            user_id: int,
            user_telegram_id: int,
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
            user_telegram_id=user_telegram_id,
            subject=support_ticket.subject,
            issue=support_ticket.issue,
            answer=support_ticket.answer,
            status=support_ticket.status,
            created_at=support_ticket.created_at,
        )

    def get_all_open(self) -> list[models.SupportTicket]:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.status != SupportTicketStatus.CLOSED)
            .order_by(SupportTicket.created_at.desc())
        )
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [
            models.SupportTicket(
                id=support_ticket.id,
                user_id=support_ticket.user_id,
                user_telegram_id=telegram_id,
                subject=support_ticket.subject,
                issue=support_ticket.issue,
                answer=support_ticket.answer,
                status=support_ticket.status,
                created_at=support_ticket.created_at,
            ) for support_ticket, telegram_id in result
        ]

    def get_all_closed(self) -> list[models.SupportTicket]:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.status == SupportTicketStatus.CLOSED)
            .order_by(SupportTicket.created_at.desc())
        )
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [
            models.SupportTicket(
                id=support_ticket.id,
                user_id=support_ticket.user_id,
                user_telegram_id=telegram_id,
                subject=support_ticket.subject,
                issue=support_ticket.issue,
                answer=support_ticket.answer,
                status=support_ticket.status,
                created_at=support_ticket.created_at,
            ) for support_ticket, telegram_id in result
        ]

    def delete_by_id(self, support_ticket_id: int) -> bool:
        statement = (
            delete(SupportTicket)
            .where(SupportTicket.id == support_ticket_id)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        return bool(result.rowcount)

    def update_support_ticket_status(
            self,
            *,
            support_ticket_id: int,
            status: models.SupportTicketStatus,
    ) -> bool:
        statement = (
            update(SupportTicket)
            .where(SupportTicket.id == support_ticket_id)
            .values(status=status)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        return bool(result.rowcount)

    def update_support_ticket_answer(
            self,
            *,
            support_ticket_id: int,
            answer: str,
    ) -> bool:
        statement = (
            update(SupportTicket)
            .where(SupportTicket.id == support_ticket_id)
            .values(answer=answer)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        return bool(result.rowcount)

    def get_latest_support_ticket_or_none(
            self,
            *,
            user_telegram_id: int,
    ) -> models.SupportTicket | None:
        statement = (
            select(SupportTicket)
            .join(User, SupportTicket.user_id == User.id)
            .where(User.telegram_id == user_telegram_id)
            .order_by(SupportTicket.created_at.desc())
            .limit(1)
        )
        with self._session_factory() as session:
            support_ticket = session.scalar(statement)
        if support_ticket is not None:
            return models.SupportTicket(
                id=support_ticket.id,
                user_id=support_ticket.user_id,
                user_telegram_id=user_telegram_id,
                subject=support_ticket.subject,
                issue=support_ticket.issue,
                answer=support_ticket.answer,
                status=support_ticket.status,
                created_at=support_ticket.created_at,
            )
