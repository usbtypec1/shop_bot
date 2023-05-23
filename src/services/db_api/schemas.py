import enum

from sqlalchemy import (
    sql,
    Column,
    Integer,
    TIMESTAMP,
    BigInteger,
    String,
    Float,
    Boolean,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship

from services.db_api import base
from services.db_api.base import Base


class BaseModel(base.Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, server_default=sql.func.now())
    updated_at = Column(TIMESTAMP, onupdate=sql.func.current_timestamp())

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id})"


class User(BaseModel):
    __tablename__ = 'user'

    telegram_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String(32), nullable=True)
    balance = Column(Float, default=0)
    is_banned = Column(Boolean, default=False)


class Category(BaseModel):
    __tablename__ = 'category'

    name = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=True)
    priority = Column(Integer, nullable=False)
    max_displayed_stock_count = Column(Integer, nullable=False)
    is_hidden = Column(Boolean, nullable=False)
    can_be_seen = Column(Boolean, nullable=False)
    subcategory = relationship(
        'Subcategory',
        backref='category',
        cascade="all, delete",
    )
    product = relationship(
        'Product',
        backref='category',
        cascade="all, delete",
    )


class Subcategory(BaseModel):
    __tablename__ = 'subcategory'

    name = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=True)
    priority = Column(Integer, nullable=False)
    max_displayed_stock_count = Column(Integer, nullable=False)
    is_hidden = Column(Boolean, nullable=False)
    can_be_seen = Column(Boolean, nullable=False)
    category_id = Column(
        Integer,
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=False,
    )
    product = relationship(
        'Product',
        backref='subcategory',
        cascade="all, delete",
    )


class Product(BaseModel):
    __tablename__ = 'product'

    category_id = Column(
        Integer,
        ForeignKey('category.id', ondelete='CASCADE'),
        nullable=False,
    )
    subcategory_id = Column(
        Integer,
        ForeignKey('subcategory.id', ondelete='CASCADE'),
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    picture = Column(String(255))
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    product_unit = relationship('ProductUnit', backref='product')

    def __repr__(self):
        return (
            f'{self.id=} '
            f'{self.category_id=} '
            f'{self.subcategory_id=} '
            f'{self.name=} '
            f'{self.description=} '
            f'{self.picture=} '
            f'{self.quantity=}'
        )

    @property
    def media_file_names(self) -> list[str]:
        return [] if self.picture is None else self.picture.split('|')

    @property
    def photo_and_video_file_names(self) -> list[str]:
        """Media file names (except GIFs) with relative order."""
        return [
            file_name for file_name in self.media_file_names
            if file_name.endswith('.jpg')
               or (
                       file_name.endswith('.mp4')
                       and not file_name.endswith('.gif.mp4')
               )
        ]

    @property
    def photo_file_names(self) -> list[str]:
        return [file_name for file_name in self.media_file_names
                if file_name.endswith('.jpg')]

    @property
    def video_file_names(self) -> list[str]:
        return [file_name for file_name in self.media_file_names
                if file_name.endswith('.mp4')
                and not file_name.endswith('.gif.mp4')]

    @property
    def animation_file_names(self) -> list[str] | None:
        return [file_name for file_name in self.media_file_names
                if file_name.endswith('.gif.mp4')]


class ProductUnit(BaseModel):
    __tablename__ = 'product_unit'
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, default='text')
    sale_id = Column(Integer, ForeignKey('sale.id'))


class Sale(BaseModel):
    __tablename__ = 'sale'
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    username = Column(String(255))
    amount = Column(Float(), nullable=False)
    quantity = Column(Integer(), nullable=False)
    payment_type = Column(String(255), nullable=False)

    product_unit = relationship(
        'ProductUnit',
        lazy=False,
        backref='sale',
        cascade='all, delete',
    )


class SupportTicketStatus(enum.Enum):
    OPEN = 'Open'
    PENDING = 'Pending'
    ON_HOLD = 'On Hold'
    CLOSED = 'Closed'


class SupportTicket(BaseModel):
    __tablename__ = 'support_tickets'

    user_id = Column(Integer, ForeignKey('user.telegram_id'), nullable=False)
    subject = Column(String(64), nullable=False)
    issue = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(
        Enum(SupportTicketStatus),
        default=SupportTicketStatus.OPEN,
        nullable=False,
    )


class SupportTicketReplySource(enum.Enum):
    USER = 'User'
    ADMIN = 'Admin'


class SupportTicketReply(BaseModel):
    __tablename__ = 'support_ticket_replies'

    support_ticket_id = Column(
        Integer,
        ForeignKey('support_tickets.id'),
        nullable=False,
    )
    source = Column(Enum(SupportTicketReplySource), nullable=False)
    text = Column(Text, nullable=False)


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
