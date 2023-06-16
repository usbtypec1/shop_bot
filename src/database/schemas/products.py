import enum

from sqlalchemy import (
    String, Column, Text, Integer, ForeignKey, Float, Enum,
    Boolean
)
from sqlalchemy.orm import relationship

from database.schemas.base import BaseModel, Base

__all__ = (
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

    product_id = Column(
        Integer,
        ForeignKey('product.id'),
        nullable=False,
        primary_key=True,
    )
    payment_method = Column(
        Enum(PaymentMethod),
        nullable=False,
        primary_key=True,
    )

    product = relationship('Product', back_populates='permitted_gateways')


class Product(BaseModel):
    __tablename__ = 'product'

    category_id = Column(
        Integer,
        ForeignKey('categories.id', ondelete='CASCADE'),
        nullable=False,
    )
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    picture = Column(String(255))
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    min_order_quantity = Column(Integer, nullable=True)
    max_order_quantity = Column(Integer, nullable=True)
    max_replacement_time_in_minutes = Column(
        Integer,
        default=15,
        nullable=False,
    )
    max_displayed_stock_count = Column(Integer, nullable=False)
    is_duplicated_stock_entries_allowed = Column(Boolean, nullable=False)
    is_hidden = Column(Boolean, nullable=False)
    can_be_purchased = Column(Boolean, nullable=False)

    permitted_gateways = relationship(
        'ProductPermittedGateway',
        back_populates='product',
    )
    category = relationship(
        'Category',
        back_populates='products',
        cascade='all, delete',
    )
    product_unit = relationship('ProductUnit', backref='product')
    cart_product = relationship('CartProduct', back_populates='product')

    def __repr__(self):
        return (
            f'{self.id=} '
            f'{self.category_id=} '
            f'{self.name=} '
            f'{self.description=} '
            f'{self.picture=} '
            f'{self.quantity=}'
        )


class ProductUnit(BaseModel):
    __tablename__ = 'product_unit'
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, default='text')
    sale_id = Column(Integer, ForeignKey('sale.id'))
