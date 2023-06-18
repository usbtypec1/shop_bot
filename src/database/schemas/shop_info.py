import enum

from sqlalchemy.orm import Mapped, mapped_column

from database.schemas.base import Base

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

    key: Mapped[ShopInfoField] = mapped_column(primary_key=True)
    value: Mapped[str]
