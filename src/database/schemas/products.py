from sqlalchemy import String, Column, Text, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship

from database.schemas.base import BaseModel

__all__ = ('Product', 'ProductUnit')


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
    cart_product = relationship('CartProduct', back_populates='product')

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
