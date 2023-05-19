from dataclasses import dataclass

__all__ = ('Category', 'Subcategory')


@dataclass(frozen=True, slots=True)
class Category:
    id: int
    name: str
    icon: str | None
    priority: int
    max_displayed_stocks_count: int
    is_hidden: bool
    can_be_seen: bool


@dataclass(frozen=True, slots=True)
class Subcategory:
    id: int
    name: str
    icon: str | None
    priority: int
    max_displayed_stocks_count: int
    is_hidden: bool
    can_be_seen: bool
    category_id: int
