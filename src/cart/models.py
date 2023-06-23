from dataclasses import dataclass
from decimal import Decimal

__all__ = (
    'Product',
    'CartProduct',
)


@dataclass(frozen=True, slots=True)
class Product:
    id: int
    name: str
    price: Decimal


@dataclass(frozen=True, slots=True)
class CartProduct:
    id: int
    product: Product
    quantity: int

    @property
    def total_cost(self) -> Decimal:
        return self.product.price * self.quantity
