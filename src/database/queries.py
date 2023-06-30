from sqlalchemy import (
    orm,
    select,
    func,
    delete,
)

from database import schemas


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


def edit_product_unit(
        session: orm.Session,
        product_unit_id: int,
        product_unit_type: str,
        content: str,
) -> None:
    product_unit = get_product_unit(session, product_unit_id)
    product_unit.content = content
    product_unit.type = product_unit_type


def edit_product_quantity(
        session: orm.Session,
        product_id: int,
        quantity_delta: int,
) -> schemas.Product | None:
    product = get_product(session, product_id)
    if product is not None:
        product.quantity += quantity_delta
    return product


def delete_product_unit(session: orm.Session, product_unit_id: int) -> None:
    statement = delete(schemas.ProductUnit).filter_by(
        id=product_unit_id)
    session.execute(statement)
