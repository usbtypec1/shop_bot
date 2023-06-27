from sqlalchemy import delete, update, select

from common.repositories import BaseRepository
from database import schemas as database_models
from services.time_utils import Period
from support.models import (
    SupportTicket,
    SupportTicketStatus,
    SupportTicketReply,
    SupportTicketReplySource,
)

__all__ = (
    'SupportTicketRepository',
    'SupportTicketReplyRepository',
)


class SupportTicketRepository(BaseRepository):

    def get_by_id(self, support_ticket_id: int) -> SupportTicket:
        statement = (
            select(database_models.SupportTicket,
                   database_models.User.telegram_id)
            .join(
                database_models.User,
                database_models.SupportTicket.user_id == database_models.User.id
            )
            .where(SupportTicket.id == support_ticket_id)
        )
        with self._session_factory() as session:
            result = session.execute(statement).first()
        support_ticket, telegram_id = result
        return SupportTicket(
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
    ) -> list[SupportTicket]:
        statement = (
            select(SupportTicket, database_models.User.telegram_id)
            .join(database_models.User,
                  database_models.SupportTicket.user_id == database_models.User.id)
            .where(database_models.User.telegram_id == user_telegram_id)
            .order_by(database_models.SupportTicket.created_at.desc())
            .limit(30)
        )
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [
            SupportTicket(
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
    ) -> SupportTicket:
        support_ticket = database_models.SupportTicket(
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
        return SupportTicket(
            id=support_ticket.id,
            user_id=support_ticket.user_id,
            user_telegram_id=user_telegram_id,
            subject=support_ticket.subject,
            issue=support_ticket.issue,
            answer=support_ticket.answer,
            status=support_ticket.status,
            created_at=support_ticket.created_at,
        )

    def get_all_open(self) -> list[SupportTicket]:
        statement = (
            select(database_models.SupportTicket,
                   database_models.User.telegram_id)
            .join(database_models.User,
                  database_models.SupportTicket.user_id == User.id)
            .where(
                database_models.SupportTicket.status != SupportTicketStatus.CLOSED)
            .order_by(database_models.SupportTicket.created_at.desc())
        )
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [
            SupportTicket(
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

    def get_all_closed(self) -> list[SupportTicket]:
        statement = (
            select(database_models.SupportTicket,
                   database_models.User.telegram_id)
            .join(database_models.User,
                  SupportTicket.user_id == database_models.User.id)
            .where(
                database_models.SupportTicket.status == SupportTicketStatus.CLOSED)
            .order_by(database_models.SupportTicket.created_at.desc())
        )
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [
            SupportTicket(
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
            delete(database_models.SupportTicket)
            .where(database_models.SupportTicket.id == support_ticket_id)
        )
        with self._session_factory() as session:
            with session.begin():
                result = session.execute(statement)
        return bool(result.rowcount)

    def update_support_ticket_status(
            self,
            *,
            support_ticket_id: int,
            status: SupportTicketStatus,
    ) -> bool:
        statement = (
            update(database_models.SupportTicket)
            .where(database_models.SupportTicket.id == support_ticket_id)
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
            update(database_models.SupportTicket)
            .where(database_models.SupportTicket.id == support_ticket_id)
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
    ) -> SupportTicket | None:
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
            return SupportTicket(
                id=support_ticket.id,
                user_id=support_ticket.user_id,
                user_telegram_id=user_telegram_id,
                subject=support_ticket.subject,
                issue=support_ticket.issue,
                answer=support_ticket.answer,
                status=support_ticket.status,
                created_at=support_ticket.created_at,
            )

    def get_support_tickets_by_filter(
            self,
            *,
            status: SupportTicketStatus,
            period: Period | None = None,
            user_telegram_id: int | None = None,
            username: str | None = None,
    ) -> list[SupportTicket]:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.status == status)
        )
        if username is not None:
            statement = statement.where(User.username == username)
        if user_telegram_id is not None:
            statement = statement.where(User.telegram_id == user_telegram_id)
        if period is not None:
            statement = statement.where(
                SupportTicket.created_at.between(
                    period.start,
                    period.end,
                ),
            )
        with self._session_factory() as session:
            result = session.execute(statement).all()
        return [
            SupportTicket(
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


class SupportTicketReplyRepository(BaseRepository):

    def create(
            self,
            *,
            support_ticket_id: int,
            source: SupportTicketReplySource,
            text: str,
    ):
        support_ticket_reply = database_models.SupportTicketReply(
            support_ticket_id=support_ticket_id,
            source=source,
            text=text
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(support_ticket_reply)
                session.flush()
                session.refresh(support_ticket_reply)
        return SupportTicketReply(
            id=support_ticket_reply.id,
            support_ticket_id=support_ticket_id,
            source=source,
            text=text,
            created_at=support_ticket_reply.created_at,
        )

    def get_by_support_ticket_id(
            self,
            support_ticket_id: int,
    ) -> list[SupportTicketReply]:
        statement = (
            select(database_models.SupportTicketReply)
            .where(
                database_models.SupportTicketReply.support_ticket_id == support_ticket_id)
            .order_by(database_models.SupportTicketReply.created_at.asc())
        )
        with self._session_factory() as session:
            result = session.scalars(statement).all()
        return [
            SupportTicketReply(
                id=support_ticket_reply.id,
                support_ticket_id=support_ticket_reply.support_ticket_id,
                source=support_ticket_reply.source,
                text=support_ticket_reply.text,
                created_at=support_ticket_reply.created_at,
            ) for support_ticket_reply in result
        ]
