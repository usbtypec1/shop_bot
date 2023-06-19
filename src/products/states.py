from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'ProductDeleteStates',
    'ProductCreateStates',
    'ProductUpdateStates',
    'EditProductUnitStates',
    'EnterProductQuantityStates',
    'AddProductUnitStates',
)


class ProductDeleteStates(StatesGroup):
    confirm = State()


class ProductCreateStates(StatesGroup):
    name = State()
    description = State()
    media = State()
    price = State()
    min_order_quantity = State()
    max_order_quantity = State()
    max_replacement_time_in_minutes = State()
    max_displayed_stock = State()
    is_duplicated_stock_entries_allowed = State()
    is_hidden = State()
    can_be_purchased = State()
    permitted_gateways = State()


class ProductUpdateStates(StatesGroup):
    name = State()
    description = State()
    media = State()
    price = State()
    min_order_quantity = State()
    max_order_quantity = State()
    max_replacement_time_in_minutes = State()
    max_displayed_stock = State()
    permitted_gateways = State()


class AddProductStates(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_picture = State()
    waiting_price = State()
    waiting_content = State()


class AddProductUnitStates(StatesGroup):
    waiting_content = State()


class EditProductUnitStates(StatesGroup):
    waiting_content = State()


class EnterProductQuantityStates(StatesGroup):
    waiting_quantity = State()
