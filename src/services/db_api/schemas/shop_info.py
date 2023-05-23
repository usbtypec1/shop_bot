import enum

from sqlalchemy import Column, Enum, Text

from services.db_api.schemas.base import Base

__all__ = (
    'ShopInfoField',
    'ShopInformation',
)


class ShopInfoField(enum.Enum):
    RULES = '📗 Rules'
    FAQ = 'ℹ️ FAQ'
    GREETINGS = '👋 Greetings'
    RETURN = '✋ Return'
    SUPPORT_RULES = '📗 Support Rules'


class ShopInformation(Base):
    __tablename__ = 'shop_information'

    key = Column(Enum(ShopInfoField), primary_key=True)
    value = Column(Text, nullable=False)
