from sqlalchemy import Column, ForeignKey, Integer, Float, String
from sqlalchemy.orm import relationship

from services.db_api.schemas.base import BaseModel

__all__ = ('Sale',)


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
