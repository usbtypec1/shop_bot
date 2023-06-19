from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from common.filters import AdminFilter
from common.views import edit_message_by_view
from products.callback_data import (
    AdminProductUpdateCallbackData,
    AdminProductPermittedGatewayChoiceCallbackData
)
from products.models import PaymentMethod
from products.repositories import ProductRepository
from products.states import ProductUpdateStates
from products.views import (
    AdminProductPermittedGatewaysView,
    AdminProductDetailView
)

__all__ = ('register_handlers',)


async def on_show_permitted_gateways_list(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductUpdateStates.permitted_gateways.set()
    product = product_repository.get_by_id(product_id)
    view = AdminProductPermittedGatewaysView(
        payment_method=PaymentMethod,
        chosen_payment_methods=product.permitted_gateways,
    )
    await state.update_data(
        product_id=product_id,
        permitted_gateways=set(product.permitted_gateways),
    )
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_permitted_gateways_choice(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    state_data = await state.get_data()
    permitted_gateways: set[PaymentMethod] = state_data['permitted_gateways']
    payment_method = callback_data['payment_method']
    if payment_method in permitted_gateways:
        permitted_gateways.remove(payment_method)
    else:
        permitted_gateways.add(payment_method)
    await state.update_data(permitted_gateways=permitted_gateways)
    view = AdminProductPermittedGatewaysView(
        payment_method=PaymentMethod,
        chosen_payment_methods=permitted_gateways,
    )
    await edit_message_by_view(message=callback_query.message, view=view)


async def on_product_permitted_gateways_update_finish(
        callback_query: CallbackQuery,
        state: FSMContext,
        product_repository: ProductRepository,
) -> None:
    state_data = await state.get_data()
    await state.finish()
    product_id: int = state_data['product_id']
    permitted_gateways: set[PaymentMethod] = state_data['permitted_gateways']
    product_repository.update_permitted_gateways(
        product_id=product_id,
        payment_methods=permitted_gateways,
    )
    product = product_repository.get_by_id(product_id)
    view = AdminProductDetailView(product)
    await edit_message_by_view(message=callback_query.message, view=view)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_callback_query_handler(
        on_show_permitted_gateways_list,
        AdminProductUpdateCallbackData().filter(field='permitted-gateways'),
        AdminFilter(),
        state='*',
    )
    dispatcher.register_callback_query_handler(
        on_permitted_gateways_choice,
        AdminFilter(),
        AdminProductPermittedGatewayChoiceCallbackData().filter(),
        state=ProductUpdateStates.permitted_gateways,
    )
    dispatcher.register_callback_query_handler(
        on_product_permitted_gateways_update_finish,
        AdminFilter(),
        Text('permitted-gateways-choose-finish'),
        state=ProductUpdateStates.permitted_gateways,
    )
