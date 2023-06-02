from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship

from database.schemas.base import BaseModel

__all__ = ('Category',)


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
