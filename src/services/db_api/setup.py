import structlog

from services.db_api.engine import engine
from services.db_api.schemas.base import Base

__all__ = ('init_tables',)

logger = structlog.get_logger('database')


def init_tables():
    Base.metadata.create_all(engine)
    logger.debug('Database tables init')
