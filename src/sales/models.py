from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from payments.models import PaymentMethod

__all__ = ('Sale', 'SoldProduct', 'PaymentMethod')


@dataclass(frozen=True, slots=True)
class SoldProduct:
    product_id: int | None
    price_at_the_moment: Decimal
    quantity: int

    @property
    def total_cost(self) -> Decimal:
        return self.price_at_the_moment * self.quantity


@dataclass(frozen=True, slots=True)
class Sale:
    id: int
    user_id: int
    payment_method: PaymentMethod
    created_at: datetime
    products: list[SoldProduct]

    def calculate_total_cost(self) -> Decimal:
        return sum(product.total_cost for product in self.products)
