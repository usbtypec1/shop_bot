import sqlalchemy
from sqlalchemy import orm, sql

from services.db_api import base


class BaseModel(base.Base):
    __abstract__ = True

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, unique=True,
                           primary_key=True, autoincrement=True)
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP,
                                   server_default=sql.func.now())
    updated_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP,
                                   onupdate=sql.func.current_timestamp())

    def __repr__(self):
        return f"{type(self).__name__}(id={self.id})"


class User(BaseModel):
    __tablename__ = 'user'
    telegram_id = sqlalchemy.Column(sqlalchemy.BigInteger(), nullable=False,
                                    unique=True)
    username = sqlalchemy.Column(sqlalchemy.String(32))
    balance = sqlalchemy.Column(sqlalchemy.Float(), default=0)
    is_banned = sqlalchemy.Column(sqlalchemy.Boolean, default=False)


class Category(BaseModel):
    __tablename__ = 'category'
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    icon = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    priority = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    max_displayed_stock_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    is_hidden = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    can_be_seen = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    subcategory = orm.relationship('Subcategory', backref='category',
                                   cascade="all, delete")
    product = orm.relationship('Product', backref='category',
                               cascade="all, delete")


class Subcategory(BaseModel):
    __tablename__ = 'subcategory'
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    icon = sqlalchemy.Column(sqlalchemy.String(255), nullable=True)
    priority = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    max_displayed_stock_count = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False
    )
    is_hidden = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    can_be_seen = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    category_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey(
            'category.id',
            ondelete='CASCADE'
        ),
        nullable=False,
    )
    product = orm.relationship(
        'Product',
        backref='subcategory',
        cascade="all, delete",
    )


class Product(BaseModel):
    __tablename__ = 'product'
    category_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('category.id', ondelete='CASCADE'), nullable=False
    )
    subcategory_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('subcategory.id', ondelete='CASCADE')
    )
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    picture = sqlalchemy.Column(sqlalchemy.String(255))
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    product_unit = orm.relationship('ProductUnit', backref='product')

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
    product_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('product.id'), nullable=False
    )
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String, default='text')
    sale_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('sale.id'))


class Sale(BaseModel):
    __tablename__ = 'sale'
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('user.id'),
                                nullable=False)
    product_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('product.id'),
                                   nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String(255))
    amount = sqlalchemy.Column(sqlalchemy.Float(), nullable=False)
    quantity = sqlalchemy.Column(sqlalchemy.Integer(), nullable=False)
    payment_type = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)

    product_unit = orm.relationship('ProductUnit', lazy=False, backref='sale',
                                    cascade='all, delete')


class SupportSubject(BaseModel):
    __tablename__ = 'support_subject'
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False,
                             unique=True)


class SupportRequest(BaseModel):
    __tablename__ = 'support_request'

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey('user.telegram_id'),
                                nullable=False)
    subject_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey('support_subject.id'))
    username = sqlalchemy.Column(sqlalchemy.String())
    is_open = sqlalchemy.Column(sqlalchemy.Boolean(), default=True)
    issue = sqlalchemy.Column(sqlalchemy.Text(), nullable=False)
    answer = sqlalchemy.Column(sqlalchemy.Text())

    subject = orm.relationship(
        'SupportSubject', lazy=False, backref='support_request',
        cascade='all, delete',
    )
    user = orm.relationship('User', backref='support_request', lazy=False)


class ShopInformation(BaseModel):
    __tablename__ = 'shop_information'

    key = sqlalchemy.Column(sqlalchemy.String())
    value = sqlalchemy.Column(sqlalchemy.String())
