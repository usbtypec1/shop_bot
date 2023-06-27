from sqlalchemy import delete, update, select

from common.models import Period
from common.repositories import BaseRepository
from database.schemas import (
    SupportTicket,
    SupportTicketReply,
    User,
    SupportTicketStatus,
)
from support import models as support_models

__all__ = (
    'SupportTicketRepository',
    'SupportTicketReplyRepository',
)


def map_support_ticket_to_dto(
        *,
        support_ticket: SupportTicket,
        user_telegram_id: int
) -> support_models.SupportTicket:
    return support_models.SupportTicket(
        id=support_ticket.id,
        user_id=support_ticket.user_id,
        user_telegram_id=user_telegram_id,
        subject=support_ticket.subject,
        issue=support_ticket.issue,
        answer=support_ticket.answer,
        status=support_ticket.status,
        created_at=support_ticket.created_at,
    )


def map_support_ticket_reply_to_dto(
        support_ticket_reply: SupportTicketReply,
) -> support_models.SupportTicketReply:
    return support_models.SupportTicketReply(
        id=support_ticket_reply.id,
        support_ticket_id=support_ticket_reply.ticket_id,
        source=support_ticket_reply.source,
        text=support_ticket_reply.text,
        created_at=support_ticket_reply.created_at,
    )


class SupportTicketRepository(BaseRepository):

    def get_by_id(self, support_ticket_id: int) -> SupportTicket:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.id == support_ticket_id)
        )
        with self._session_factory() as session:
            result = session.execute(statement).first()
        support_ticket, user_telegram_id = result
        return map_support_ticket_to_dto(
            support_ticket=support_ticket,
            user_telegram_id=user_telegram_id,
        )

    def get_by_user_telegram_id(
            self,
            user_telegram_id: int,
    ) -> list[SupportTicket]:
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
            map_support_ticket_to_dto(
                support_ticket=support_ticket,
                user_telegram_id=user_telegram_id,
            ) for support_ticket, user_telegram_id in result
        ]

    def create(
            self,
            *,
            user_id: int,
            user_telegram_id: int,
            subject: str,
            issue: str,
    ) -> SupportTicket:
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
        return map_support_ticket_to_dto(
            support_ticket=support_ticket,
            user_telegram_id=user_telegram_id,
        )

    def get_all_open(self) -> list[SupportTicket]:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.status != SupportTicketStatus.CLOSED)
            .order_by(SupportTicket.created_at.desc())
        )
        with self._session_factory() as session:
            support_tickets = session.execute(statement).all()
        return [
            map_support_ticket_to_dto(
                support_ticket=support_ticket,
                user_telegram_id=user_telegram_id,
            ) for support_ticket, user_telegram_id in support_tickets
        ]

    def get_all_closed(self) -> list[SupportTicket]:
        statement = (
            select(SupportTicket, User.telegram_id)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.status == SupportTicketStatus.CLOSED)
            .order_by(SupportTicket.created_at.desc())
        )
        with self._session_factory() as session:
            support_tickets = session.execute(statement).all()
        return [
            map_support_ticket_to_dto(
                support_ticket=support_ticket,
                user_telegram_id=user_telegram_id,
            ) for support_ticket, user_telegram_id in support_tickets
        ]

    def delete_by_id(self, support_ticket_id: int):
        delete_replies_statement = (
            delete(SupportTicketReply)
            .where(SupportTicketReply.ticket_id == support_ticket_id)
        )
        delete_ticket_statement = (
            delete(SupportTicket)
            .where(SupportTicket.id == support_ticket_id)
        )
        with self._session_factory() as session:
            with session.begin():
                session.execute(delete_replies_statement)
                session.execute(delete_ticket_statement)

    def update_support_ticket_status(
            self,
            *,
            support_ticket_id: int,
            status: SupportTicketStatus,
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
            return map_support_ticket_to_dto(
                support_ticket=support_ticket,
                user_telegram_id=user_telegram_id,
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
            support_tickets = session.execute(statement).all()
        return [
            map_support_ticket_to_dto(
                support_ticket=support_ticket,
                user_telegram_id=user_telegram_id
            ) for support_ticket, user_telegram_id in support_tickets
        ]


class SupportTicketReplyRepository(BaseRepository):

    def create(
            self,
            *,
            support_ticket_id: int,
            source: support_models.SupportTicketReplySource,
            text: str,
    ):
        support_ticket_reply = SupportTicketReply(
            ticket_id=support_ticket_id,
            source=source,
            text=text
        )
        with self._session_factory() as session:
            with session.begin():
                session.add(support_ticket_reply)
                session.flush()
                session.refresh(support_ticket_reply)
        return map_support_ticket_reply_to_dto(support_ticket_reply)

    def get_by_support_ticket_id(
            self,
            support_ticket_id: int,
    ) -> list[support_models.SupportTicketReply]:
        statement = (
            select(SupportTicketReply)
            .where(SupportTicketReply.ticket_id == support_ticket_id)
            .order_by(SupportTicketReply.created_at.asc())
        )
        with self._session_factory() as session:
            result = session.scalars(statement).all()
        return [
            map_support_ticket_reply_to_dto(support_ticket_reply)
            for support_ticket_reply in result
        ]
