from aiogram.dispatcher.filters.state import StatesGroup, State

__all__ = (
    'ProductCreateStates',
    'EditProductUnitStates',
    'EditProductPictureStates',
    'EditProductPriceStates',
    'EditProductTitleStates',
    'EditProductDescriptionStates',
    'EnterProductQuantityStates',
    'AddProductStates',
    'AddProductUnitStates',
)


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


class AddProductStates(StatesGroup):
    waiting_name = State()
    waiting_description = State()
    waiting_picture = State()
    waiting_price = State()
    waiting_content = State()


class EditProductTitleStates(StatesGroup):
    waiting_title = State()


class EditProductDescriptionStates(StatesGroup):
    waiting_description = State()


class EditProductPictureStates(StatesGroup):
    waiting_picture = State()


class EditProductPriceStates(StatesGroup):
    waiting_price = State()


class AddProductUnitStates(StatesGroup):
    waiting_content = State()


class EditProductUnitStates(StatesGroup):
    waiting_content = State()


class EnterProductQuantityStates(StatesGroup):
    waiting_quantity = State()
