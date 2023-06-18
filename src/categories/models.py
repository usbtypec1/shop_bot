from dataclasses import dataclass

__all__ = ('Category',)


@dataclass(frozen=True, slots=True)
class Category:
    id: int
    name: str
    icon: str | None
    priority: int
    max_displayed_stock_count: int
    is_hidden: bool
    can_be_seen: bool
    parent_id: int | None

    @property
    def name_display(self) -> str:
        return self.name if self.icon is None else f'{self.icon} {self.name}'
