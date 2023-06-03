from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database.schemas.base import BaseModel

__all__ = ('Category',)


class Category(BaseModel):
    __tablename__ = 'categories'

    name = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=True)
    priority = Column(Integer, nullable=False)
    max_displayed_stock_count = Column(Integer, nullable=False)
    is_hidden = Column(Boolean, nullable=False)
    can_be_seen = Column(Boolean, nullable=False)
    parent_id = Column(
        Integer,
        ForeignKey('categories.id'),
        nullable=True,
    )

    parent = relationship(
        'Category',
        back_populates='parent',
        cascade='all, delete',
    )
    product = relationship(
        'Product',
        backref='category',
        cascade="all, delete",
    )
