from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery, ChatType, Message, Update, ContentType

from cart.repositories import CartRepository
from cart.services import validate_product_quantity_change
from common.views import answer_view
from products.callback_data import UserProductBuyCallbackData
from products.exceptions import ProductQuantityValidationError
from products.repositories import ProductRepository
from products.services import parse_product_quantity, calculate_total_cost
from products.states import ProductBuyStates
from sales.models import PaymentMethod

__all__ = ('register_handlers',)

from sales.repositories import SaleRepository

from sales.views import UserProductBuyChoosePaymentMethodView
from users.repositories import UserRepository
from users.services import validate_user_balance


async def on_product_quantity_validation_error(
        update: Update,
        exception: ProductQuantityValidationError,
) -> bool:
    if update.message is not None:
        await update.message.answer(str(exception))
    return True


async def on_start_buy_product_flow(
        callback_query: CallbackQuery,
        callback_data: dict,
        state: FSMContext,
) -> None:
    product_id: int = callback_data['product_id']
    await ProductBuyStates.quantity.set()
    await state.update_data(product_id=product_id)
    await callback_query.message.answer('Enter number of pieces')


async def on_product_quantity_to_buy_input(
        message: Message,
        state: FSMContext,
        product_repository: ProductRepository,
        cart_repository: CartRepository,
        user_repository: UserRepository,
) -> None:
    state_data = await state.get_data()
    product_id: int = state_data['product_id']
    quantity = parse_product_quantity(message.text)
    await ProductBuyStates.payment_method.set()
    await state.update_data(quantity=quantity)
    product = product_repository.get_by_id(product_id)
    user = user_repository.get_by_telegram_id(message.from_user.id)
    cart_repository.create(
        user_id=user.id,
        product_id=product_id,
        quantity=quantity
    )
    view = UserProductBuyChoosePaymentMethodView(product.permitted_gateways)
    await answer_view(message=message, view=view)


async def on_pay_via_balance(
        callback_query: CallbackQuery,
        state: FSMContext,
        cart_repository: CartRepository,
        user_repository: UserRepository,
        product_repository: ProductRepository,
        sale_repository: SaleRepository,
) -> None:
    payment_method = PaymentMethod[callback_query.data]
    state_data = await state.get_data()
    product_id: int = state_data['product_id']
    quantity: int = state_data['quantity']

    user = user_repository.get_by_telegram_id(callback_query.from_user.id)
    product = product_repository.get_by_id(product_id)

    validate_product_quantity_change(
        product=product,
        cart_product_quantity=0,
        will_be_changed_to=quantity,
    )
    cart_products = cart_repository.get_cart_products(
        user_telegram_id=callback_query.from_user.id,
    )
    total_cost = calculate_total_cost(cart_products)

    validate_user_balance(user=user, amount_to_subtract=total_cost)

    try:
        sale = sale_repository.create_and_subtract_from_balance(
            user_id=user.id,
            cart_products=cart_products,
            payment_method=payment_method,
        )
        print(sale)
    except Exception:
        cart_repository.delete_by_id(created_cart_product_id)


async def on_pay_via_coinbase(
        callback_query: CallbackQuery,
) -> None:
    await callback_query.answer('Not implemented', show_alert=True)


async def on_pay_via_admin(
        callback_query: CallbackQuery,
) -> None:
    await callback_query.answer('Not implemented', show_alert=True)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_errors_handler(
        on_product_quantity_validation_error,
        exception=ProductQuantityValidationError,
    )
    dispatcher.register_callback_query_handler(
        on_start_buy_product_flow,
        UserProductBuyCallbackData().filter(),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        on_product_quantity_to_buy_input,
        chat_type=ChatType.PRIVATE,
        content_types=ContentType.TEXT,
        state=ProductBuyStates.quantity,
    )
    dispatcher.register_callback_query_handler(
        on_pay_via_balance,
        Text(PaymentMethod.BALANCE.name),
        chat_type=ChatType.PRIVATE,
        state=ProductBuyStates.payment_method,
    )
    dispatcher.register_callback_query_handler(
        on_pay_via_admin,
        Text(PaymentMethod.FROM_ADMIN.name),
        chat_type=ChatType.PRIVATE,
        state=ProductBuyStates.payment_method,
    )
    dispatcher.register_callback_query_handler(
        on_pay_via_coinbase,
        Text(PaymentMethod.COINBASE.name),
        chat_type=ChatType.PRIVATE,
        state=ProductBuyStates.payment_method,
    )
