import contextlib

from sqlalchemy.orm import sessionmaker, Session

from services.db_api.engine import engine

__all__ = (
    'session_factory',
    'create_session',
    'RawSession',
)


# TODO Delete it
RawSession = sessionmaker(bind=engine.engine)

session_factory = sessionmaker(bind=engine, expire_on_commit=False)


@contextlib.contextmanager
def create_session() -> Session:
    with RawSession() as session, session.begin():
        yield session
