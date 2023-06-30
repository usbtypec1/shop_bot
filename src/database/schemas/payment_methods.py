import enum

__all__ = ('PaymentMethod',)


class PaymentMethod(enum.Enum):
    COINBASE = 'Coinbase'
    FROM_ADMIN = 'From Admin'
    BALANCE = 'Balance'
