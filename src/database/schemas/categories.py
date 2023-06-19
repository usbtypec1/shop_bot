from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from database.schemas.base import BaseModel

__all__ = ('Category',)


class Category(BaseModel):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    icon: Mapped[str | None]
    priority: Mapped[int]
    max_displayed_stock_count: Mapped[int]
    is_hidden: Mapped[bool]
    can_be_seen: Mapped[bool]
    parent_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('categories.id', ondelete='CASCADE'),
        nullable=True,
    )

    parent: Mapped['Category'] = relationship(
        'Category',
        backref='children',
        cascade='all, delete',
        remote_side=[id]
    )
    products: Mapped[list['Product']] = relationship(
        'Product',
        back_populates='category',
        cascade="all, delete",
    )
