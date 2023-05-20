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
)
from sqlalchemy.orm import relationship

from services.db_api import base


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


class SupportSubject(BaseModel):
    __tablename__ = 'support_subject'
    name = Column(String(255), nullable=False, unique=True)


class SupportRequest(BaseModel):
    __tablename__ = 'support_request'

    user_id = Column(Integer, ForeignKey('user.telegram_id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('support_subject.id'))
    username = Column(String)
    is_open = Column(Boolean, default=True)
    issue = Column(Text, nullable=False)
    answer = Column(Text)

    subject = relationship(
        'SupportSubject',
        lazy=False,
        backref='support_request',
        cascade='all, delete',
    )
    user = relationship('User', backref='support_request', lazy=False)


class ShopInformation(BaseModel):
    __tablename__ = 'shop_information'

    key = Column(String)
    value = Column(String)
