from sqlalchemy import BigInteger, Column, Float, String, Boolean

from services.db_api.schemas.base import BaseModel

__all__ = ('User',)


class User(BaseModel):
    __tablename__ = 'user'

    telegram_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String(32), nullable=True)
    balance = Column(Float, default=0)
    is_banned = Column(Boolean, default=False)
