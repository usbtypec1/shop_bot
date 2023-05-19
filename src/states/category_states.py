from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import StatesGroup, State


class CategoryCreateStates(StatesGroup):
    name = State()
    icon = State()
    priority = State()
    are_stocks_displayed = State()
    is_hidden = State()
    can_be_seen = State()


# TODO Delete all this crap below
class AddCategories(state.StatesGroup):
    waiting_category_name = state.State()


class AddSubcategories(state.StatesGroup):
    waiting_subcategory_name = state.State()

class EditCategories(state.StatesGroup):
    waiting_new_category_name = state.State()

class EditSubcategories(state.StatesGroup):
    waiting_subcategory_id = state.State()
    waiting_new_subcategory_name = state.State()

class DeleteConfirm(state.StatesGroup):
    waiting_for_delete_category_confirm = state.State()
    waiting_for_delete_subcategory_confirm = state.State()

class DeleteSubcategoryConfirm(state.StatesGroup):
    waiting_for_delete_subcategory_id = state.State()