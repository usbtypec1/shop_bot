import enum
from decimal import Decimal
from uuid import UUID

from sqlalchemy import String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.schemas.base import BaseModel, Base

__all__ = (
    'ProductMedia',
    'MediaType',
    'Product',
    'ProductUnit',
    'ProductPermittedGateway',
    'PaymentMethod',
)


class PaymentMethod(enum.Enum):
    COINBASE = 'Coinbase'
    FROM_ADMIN = 'From Admin'
    BALANCE = 'Balance'


class ProductPermittedGateway(Base):
    __tablename__ = 'product_permitted_gateways'

    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id', ondelete='CASCADE'),
        primary_key=True,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(primary_key=True)

    product = relationship(
        'Product',
        back_populates='permitted_gateways',
        cascade='all, delete'
    )


class MediaType(enum.IntEnum):
    PHOTO = 1
    VIDEO = 2
    ANIMATION = 3


class ProductMedia(Base):
    __tablename__ = 'product_media'

    uuid: Mapped[UUID] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey('products.id', ondelete='CASCADE'),
    )
    type: Mapped[MediaType]

    product = relationship(
        'Product',
        back_populates='media',
        cascade='all, delete',
    )


class Product(BaseModel):
    __tablename__ = 'products'

    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='CASCADE'),
    )
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str]
    price: Mapped[Decimal]
    quantity: Mapped[int] = mapped_column(default=0)
    min_order_quantity: Mapped[int | None]
    max_order_quantity: Mapped[int | None]
    max_replacement_time_in_minutes: Mapped[int]
    max_displayed_stock_count: Mapped[int | None]
    is_duplicated_stock_entries_allowed: Mapped[bool]
    is_hidden: Mapped[bool]
    can_be_purchased: Mapped[bool]

    permitted_gateways: Mapped[list[ProductPermittedGateway]] = relationship(
        'ProductPermittedGateway',
        back_populates='product',
    )
    category: Mapped['Category'] = relationship(
        'Category',
        back_populates='products',
        cascade='all, delete',
    )
    units: Mapped['ProductUnit'] = relationship(
        'ProductUnit',
        back_populates='product',
    )
    cart_products: Mapped[list['CartProduct']] = relationship(
        'CartProduct',
        back_populates='product',
    )
    media: Mapped[list[ProductMedia]] = relationship(
        'ProductMedia',
        back_populates='product',
    )

    __table_args__ = (
        CheckConstraint(
            'quantity >= 0',
            name='check_product_quantity_non_negative'
        ),
    )


class ProductUnit(BaseModel):
    __tablename__ = 'product_units'
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    content: Mapped[str]
    type: Mapped[str]
    sale_id: Mapped[int] = mapped_column(ForeignKey('sale.id'))

    product: Mapped[Product] = relationship('Product', back_populates='units')
