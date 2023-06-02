import decimal

from sqlalchemy import (
    orm,
    exists,
    select,
    func,
    delete,
    literal_column,
    literal,
)

from database import schemas


def add_product(
        session: orm.Session,
        name: str,
        description: str,
        price: float,
        quantity: int,
        pictures: Iterable[str],
        category_id: int,
        subcategory_id: int = None,
) -> schemas.Product:
    # Concatenate pictures list to string
    # so we can store multiple media files in string column in DB
    picture = '|'.join(pictures) or None

    product = schemas.Product(
        category_id=category_id,
        subcategory_id=subcategory_id,
        name=name, description=description,
        picture=picture, price=price, quantity=quantity
    )
    session.add(product)
    session.flush()
    session.refresh(product)
    return product


def add_product_unit(
        session: orm.Session,
        product_id: int,
        content_type: str,
        content: str,
) -> schemas.ProductUnit:
    product_unit = schemas.ProductUnit(
        product_id=product_id,
        content=content,
        type=content_type
    )
    session.add(product_unit)
    session.flush()
    session.refresh(product_unit)
    return product_unit


def add_sale(
        session: orm.Session,
        user_id: int,
        username: str,
        product_id: int,
        amount: float,
        quantity: int,
        payment_type: str,
) -> schemas.Sale:
    sale = schemas.Sale(
        user_id=user_id,
        product_id=product_id,
        username=username,
        amount=amount,
        quantity=quantity,
        payment_type=payment_type,
    )
    session.add(sale)
    session.flush()
    session.refresh(sale)
    return sale


def get_users(
        session: orm.Session,
        limit: int = None,
        offset: int = None,
        usernames: list[str] = (),
        ids: list[int] = (),
) -> list[schemas.User]:
    statement = select(schemas.User)
    if len(usernames) > 0:
        statement = statement.filter(schemas.User.username.in_(usernames))
    if len(ids) > 0:
        statement = statement.filter(schemas.User.id.in_(ids))
    if limit is not None:
        statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)
    return session.scalars(statement).all()


def get_buyers(
        session: orm.Session
) -> list[tuple[int, str | None, int, float]]:
    statement = select(
        schemas.User.telegram_id, schemas.User.username,
        func.sum(schemas.Sale.quantity),
        func.sum(schemas.Sale.amount)
    ).join(schemas.Sale)
    statement = statement.group_by(schemas.User.id)
    return session.execute(statement).all()


def get_users_telegram_id(session: orm.Session) -> list[int]:
    return session.scalars(select(schemas.User.telegram_id)).all()


def get_user(session: orm.Session, user_id: int = None,
             telegram_id: int = None) -> schemas.User | None:
    statement = select(schemas.User)
    if user_id is not None:
        statement = statement.filter_by(id=user_id)
    elif telegram_id is not None:
        statement = statement.filter_by(telegram_id=telegram_id)
    else:
        return None
    return session.scalars(statement).first()


def get_all_categories(session: orm.Session) -> list[schemas.Category]:
    return session.scalars(select(schemas.Category)).all()


def get_category_items(
        session: orm.Session,
        category_id: int,
        limit: int | None = None,
        offset: int | None = None,
) -> list[tuple[int, str, str]]:
    statement = select(
        schemas.Product.id,
        literal_column('product.name') + ' | $' +
        literal_column('product.price') + ' | ' +
        literal_column('product.quantity') + ' pc(s)',
        literal('product')).filter_by(
        category_id=category_id, subcategory_id=None
    )
    if limit is not None:
        statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)
    return session.execute(statement).all()


def get_category_products(
        session: orm.Session,
        category_id: int = None,
        subcategory_id: int = None,
        limit: int = None,
        offset: int = None,
) -> list[schemas.Product]:
    if subcategory_id:
        statement = select(schemas.Product).filter_by(
            subcategory_id=subcategory_id)
    else:
        statement = select(schemas.Product).filter_by(
            category_id=category_id, subcategory_id=None
        )
    if limit is not None:
        statement = statement.limit(limit)
        if offset is not None:
            statement = statement.offset(offset)
    categories = session.scalars(statement).all()
    return categories


def get_product(
        session: orm.Session,
        product_id: int,
) -> schemas.Product | None:
    return session.get(schemas.Product, product_id)


def get_product_unit(
        session: orm.Session,
        product_unit_id: int,
) -> schemas.ProductUnit | None:
    return session.get(schemas.ProductUnit, product_unit_id)


def get_not_sold_product_units(
        session: orm.Session,
        product_id: int,
        quantity: int = None,
) -> list[schemas.ProductUnit]:
    statement = select(schemas.ProductUnit).filter_by(
        product_id=product_id, sale_id=None)
    if quantity is not None:
        statement = statement.limit(quantity)
    return session.scalars(statement).all()


def get_purchases(
        session: orm.Session,
        user_id: int = None,
        limit: int = None,
        offset: int = None,
) -> list[tuple[str, int, float]]:
    statement = select(
        schemas.Product.name,
        func.sum(schemas.Sale.quantity),
        func.sum(schemas.Sale.amount)
    ).join(schemas.Sale).group_by(schemas.Sale.product_id)
    if user_id is not None:
        statement = statement.filter(schemas.Sale.user_id == user_id)
    if limit is not None:
        statement = statement.limit(limit)
    if offset is not None:
        statement = statement.offset(offset)
    statement = statement.order_by(schemas.Sale.created_at.desc())
    return session.execute(statement).all()


def get_support_request(
        session: orm.Session,
        support_request_id: int,
) -> schemas.SupportTicket:
    return session.get(schemas.SupportTicket, support_request_id)


def get_user_support_requests(
        session: orm.Session,
        user_id: int,
) -> list[schemas.SupportTicket]:
    statement = select(schemas.SupportTicket).filter_by(
        user_id=user_id)
    return session.scalars(statement).all()


def ban_user(session: orm.Session, user_id: int) -> schemas.User | None:
    user = get_user(session, user_id)
    if user is not None:
        user.is_banned = True
        return user


def unban_user(session: orm.Session, user_id: int) -> schemas.User | None:
    user = get_user(session, user_id)
    if user is not None:
        user.is_banned = False
        return user


def top_up_balance(
        session: orm.Session,
        user_id: int,
        balance_delta: float | decimal.Decimal,
) -> None:
    user = get_user(session, user_id)
    if isinstance(balance_delta, float):
        balance_delta = decimal.Decimal(str(balance_delta))
    if user is not None:
        balance = decimal.Decimal(str(user.balance)) + balance_delta
        user.balance = float(balance)


def update_balance(
        session: orm.Session,
        user_id: int,
        new_balance: float,
) -> None:
    user = get_user(session, user_id)
    if user is not None:
        user.balance = new_balance


def edit_product_unit(
        session: orm.Session,
        product_unit_id: int,
        product_unit_type: str,
        content: str,
) -> None:
    product_unit = get_product_unit(session, product_unit_id)
    product_unit.content = content
    product_unit.type = product_unit_type


def add_sold_product_unit(
        session: orm.Session,
        sale_id: int,
        product_unit_id: int,
) -> None:
    product_unit = get_product_unit(session, product_unit_id)
    product_unit.sale_id = sale_id


def edit_product_name(
        session: orm.Session,
        product_id: int,
        name: str,
) -> schemas.Product | None:
    product = get_product(session, product_id)
    if product is not None:
        product.name = name
    return product


def edit_product_description(
        session: orm.Session,
        product_id: int,
        description: str,
) -> schemas.Product | None:
    product = get_product(session, product_id)
    if product is not None:
        product.description = description
    return product


def edit_product_picture(
        session: orm.Session,
        product_id: int,
        picture: str | None,
) -> schemas.Product | None:
    product = get_product(session, product_id)
    if product:
        product.picture = picture
    return product


def edit_product_price(
        session: orm.Session,
        product_id: int,
        price: float,
) -> schemas.Product | None:
    product = get_product(session, product_id)
    if product is not None:
        product.price = price
    return product


def edit_product_quantity(
        session: orm.Session,
        product_id: int,
        quantity_delta: int,
) -> schemas.Product | None:
    product = get_product(session, product_id)
    if product is not None:
        product.quantity += quantity_delta
    return product


def reset_product_quantity(
        session: orm.Session,
        product_id: int,
) -> schemas.Product | None:
    product = get_product(session, product_id)
    if product is not None:
        product.quantity = 0
    return product


def delete_product(session: orm.Session, product_id: int) -> None:
    session.execute(delete(schemas.Product).filter_by(id=product_id))


def delete_product_unit(session: orm.Session, product_unit_id: int) -> None:
    statement = delete(schemas.ProductUnit).filter_by(
        id=product_unit_id)
    session.execute(statement)


def delete_not_sold_product_units(session: orm.Session,
                                  product_id: int) -> None:
    statement = delete(schemas.ProductUnit).filter_by(
        product_id=product_id, sale_id=None)
    session.execute(statement)


def count_users(session: orm.Session) -> int:
    return session.scalar(
        select(func.count(schemas.User.id)))


def count_user_orders(session: orm.Session, user_id: int) -> int:
    statement = select(
        func.count(schemas.Sale.id)).filter_by(
        user_id=user_id
    )
    return session.scalar(statement)


def count_purchases(session: orm.Session) -> int:
    statement = select(func.sum(schemas.Sale.quantity))
    return session.scalar(statement) or 0


def count_user_purchases(session: orm.Session, user_id: int) -> int:
    statement = select(func.sum(schemas.Sale.quantity))
    statement = statement.filter(schemas.Sale.user_id == user_id)
    return session.scalar(statement) or 0


def get_total_orders_amount(session: orm.Session) -> float:
    return session.scalar(
        select(func.sum(schemas.Sale.amount))) or 0


def get_user_orders_amount(session: orm.Session, user_id: int):
    statement = select(func.sum(schemas.Sale.amount))
    return session.scalar(
        statement.filter(schemas.Sale.user_id == user_id)) or 0


## to get the user's balance in src/handlers/users/profile.py
def get_user_balance(session: orm.Session, user_id: int) -> float:
    return session.query(schemas.User.balance).filter(
        schemas.User.id == user_id).scalar()


def check_is_user_exists(session: orm.Session, telegram_id: int) -> bool:
    statement = exists(
        select(schemas.User).filter_by(telegram_id=telegram_id))
    return session.scalar(statement.select())


def check_is_user_banned(session: orm.Session, telegram_id: int) -> bool:
    statement = exists(
        select(schemas.User).filter_by(telegram_id=telegram_id,
                                       is_banned=True))
    return session.scalar(statement.select())
