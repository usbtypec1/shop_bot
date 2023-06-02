from sqlalchemy import BigInteger, Column, Float, String, Boolean
from sqlalchemy.orm import relationship

from database.schemas.base import BaseModel

__all__ = ('User',)


class User(BaseModel):
    __tablename__ = 'user'

    telegram_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String(32), nullable=True)
    balance = Column(Float, default=0)
    is_banned = Column(Boolean, default=False)

    cart_products = relationship('CartProduct', back_populates='user')
