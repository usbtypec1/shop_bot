from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from services.db_api.schemas.base import BaseModel

__all__ = ('Subcategory',)


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
