import contextlib
import decimal

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ChatType, CallbackQuery, Message

import config
import database
import responses.payments
import responses.products
from categories.repositories import CategoryRepository
from database import queries
from keyboards.inline.callback_factories import BuyProductCallbackFactory
from products.callback_data import ProductCallbackFactory
from products.states import EnterProductQuantityStates
from services import notifications
from services.payments_apis import coinbase_api
from users.exceptions import UserNotInDatabase


async def on_show_categories_to_user(
        message: Message,
        state: FSMContext,
) -> None:
    await state.finish()
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise UserNotInDatabase
        category_list = queries.get_all_categories(session)
        await responses.products.CategoriesResponses(message, category_list)


async def categories(query: CallbackQuery):
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
        category_list = queries.get_all_categories(session)
        await responses.products.CategoriesResponses(query, category_list)


async def category_items(
        query: CallbackQuery,
        callback_data: dict[str, str],
        category_repository: CategoryRepository,
):
    category_id = int(callback_data['category_id'])

    category = category_repository.get_by_id(category_id)
    subcategories = category_repository.get_subcategories(category_id)

    if not category.can_be_seen:
        await query.answer('Coming soon...', show_alert=True)
        return

    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
        category_item_list = queries.get_category_items(session, category_id)
        await responses.products.CategoryItemsResponse(
            update=query,
            subcategories=subcategories,
            products=category_item_list,
            category_id=category_id,
        )


async def subcategory_products(
        query: CallbackQuery,
        callback_data: dict[str, str],
        category_repository: CategoryRepository,
):
    category_id = int(callback_data['category_id'])
    subcategory_id = callback_data['subcategory_id']
    subcategory_id = int(subcategory_id) if subcategory_id != '' else None

    subcategory = category_repository.get_by_id(subcategory_id)

    if not subcategory.can_be_seen:
        await query.answer('Coming soon...', show_alert=True)
        return

    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
        products = queries.get_category_products(session, category_id,
                                                 subcategory_id)
        await responses.products.SubcategoryProductsResponse(
            query, category_id, subcategory_id, products
        )


async def product_menu(query: CallbackQuery,
                       callback_data: dict[str, str]):
    product_id = int(callback_data['product_id'])
    subcategory_id = callback_data['subcategory_id']
    category_id = int(callback_data['category_id'])
    subcategory_id = subcategory_id if subcategory_id != '' else None
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
        product = queries.get_product(session, product_id)
        product_pictures = product.picture
        if product_pictures:
            with contextlib.ExitStack() as exit_stack:
                files_io = [
                    exit_stack.enter_context(
                        open(config.PRODUCT_PICTURE_PATH / picture, 'rb')
                    )
                    for picture in product_pictures.split('|')
                ]
                await responses.products.ProductResponse(
                    query, product, product.quantity,
                    category_id, subcategory_id, files_io,
                )
        else:
            await responses.products.ProductResponse(
                query, product, product.quantity,
                category_id, subcategory_id, None,
            )


async def product_quantity(query: CallbackQuery,
                           callback_data: dict[str, str]):
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
    await responses.products.ProductQuantityResponse(
        query, int(callback_data['product_id']),
        int(callback_data['available_quantity'])
    )


async def own_product_quantity(
        query: CallbackQuery,
        callback_data: dict[str, str],
        state: FSMContext,
):
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, query.from_user.id):
            raise UserNotInDatabase
    await EnterProductQuantityStates.waiting_quantity.set()
    await state.update_data(callback_data=callback_data)
    await responses.products.AnotherProductQuantityResponse(
        query, int(callback_data['available_quantity'])
    )


async def a_product_quantity(
        callback_query: CallbackQuery,
        callback_data: dict[str: str],
):
    with database.create_session() as session:
        if not queries.check_is_user_exists(
                session,
                callback_query.from_user.id,
        ):
            raise UserNotInDatabase
    await responses.products.PaymentMethodResponse(
        callback_query, callback_data,
        crypto_payments=config.PaymentsSettings().crypto_payments
    )


async def another_product_quantity(
        message: Message,
        state: FSMContext,
) -> None:
    with database.create_session() as session:
        if not queries.check_is_user_exists(session, message.from_user.id):
            raise UserNotInDatabase
    quantity = message.text
    callback_data = (await state.get_data())['callback_data']
    await state.finish()
    if isinstance(quantity, str) and quantity.isdigit() and int(quantity) > 0:
        await responses.products.PaymentMethodResponse(
            message, callback_data,
            crypto_payments=config.PaymentsSettings().crypto_payments
        )
    else:
        await responses.products.IncorrectQuantity(message)


async def pay_with_qiwi(callback_query: CallbackQuery) -> None:
    await callback_query.message.answer('🚧 Under Development')


async def pay_with_yoomoney(callback_query: CallbackQuery):
    await callback_query.message.answer('🚧 Under Development')


async def pay_with_minerlock(callback_query: CallbackQuery):
    await callback_query.message.answer('🚧 Under Development')


async def pay_with_coinpayments(callback_query: CallbackQuery):
    await callback_query.message.answer('🚧 Under Development')


async def pay_with_coinbase(
        callback_query: CallbackQuery,
        callback_data: dict[str: str],
) -> None:
    with database.create_session() as session:
        user = queries.get_user(
            session,
            telegram_id=callback_query.from_user.id,
        )
        if user is None:
            raise UserNotInDatabase
        product = queries.get_product(session, int(callback_data['product_id']))
        quantity = int(callback_data['quantity'])
        amount = float(quantity * decimal.Decimal(str(product.price)))
        api = coinbase_api.CoinbaseAPI(config.CoinbaseSettings().api_key)
        # charge = api.create_charge(product.name, amount, product.description)
        charge = api.create_charge(product.name, amount,
                                   product.description[:199] if len(
                                       product.description) > 199 else product.description)
        payment_message = await responses.payments.CoinbasePaymentLinkResponse(
            callback_query, amount, quantity, charge['hosted_url'])
        if await api.check_payment(charge):
            sale = queries.add_sale(
                session, user.id, user.username, product.id,
                amount, quantity, payment_type='coinbase')
            product_units = queries.get_not_sold_product_units(session,
                                                               product.id,
                                                               quantity)
            with session.begin_nested():
                queries.edit_product_quantity(session, product.id, -quantity)
                for product_unit in product_units:
                    queries.add_sold_product_unit(session, sale.id,
                                                  product_unit.id)
            session.expunge_all()
            session.commit()
            await responses.payments.PurchaseInformationResponse(
                callback_query, sale.id, product.name, quantity, amount,
                product_units
            )
            await notifications.NewPurchaseNotification(sale, '🌐 Coinbase',
                                                        product.name,
                                                        product_units).send()
        else:
            await responses.payments.FailedPurchaseResponse(payment_message)


async def pay_with_balance(
        callback_query: CallbackQuery,
        callback_data: dict[str: str],
) -> None:
    with database.create_session() as session:
        product = queries.get_product(session, int(callback_data['product_id']))
        quantity = int(callback_data['quantity'])
        amount = float(quantity * decimal.Decimal(str(product.price)))
        user = queries.get_user(session,
                                telegram_id=int(callback_query.from_user.id))
        if user is None:
            raise UserNotInDatabase
        if user.balance >= amount:
            product_units = queries.get_not_sold_product_units(session,
                                                               product.id,
                                                               quantity)
            user = queries.get_user(session,
                                    telegram_id=callback_query.from_user.id)
            quantity = len(product_units)
            sale = queries.add_sale(
                session, user.id, user.username,
                product.id, amount, quantity, payment_type='balance'
            )
            with session.begin_nested():
                queries.edit_product_quantity(session, product.id, -quantity)
                queries.top_up_balance(session, user.id, -amount)
                for product_unit in product_units:
                    queries.add_sold_product_unit(session, sale.id,
                                                  product_unit.id)
            session.expunge_all()
            session.commit()
            await responses.payments.PurchaseInformationResponse(
                callback_query, sale.id, product.name, quantity, amount,
                product_units
            )
            await notifications.NewPurchaseNotification(sale, '💲 Balance',
                                                        product.name,
                                                        product_units).send()
        else:
            await responses.payments.NotEnoughBalanceResponse(callback_query)


def register_handlers(dispatcher: Dispatcher) -> None:
    dispatcher.register_message_handler(
        on_show_categories_to_user,
        Text('🛒 Products'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        categories,
        ProductCallbackFactory().filter(
            action='buy',
            category_id='',
            subcategory_id='',
            product_id='',
        ),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        category_items,
        ProductCallbackFactory().filter(
            action='buy', subcategory_id='', product_id=''),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        subcategory_products,
        ProductCallbackFactory().filter(action='buy', product_id=''),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        product_menu,
        ProductCallbackFactory().filter(action='buy'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        product_quantity,
        BuyProductCallbackFactory().filter(quantity='', payment_method=''),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        own_product_quantity,
        BuyProductCallbackFactory().filter(
            quantity='another',
            payment_method='',
        ),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        a_product_quantity,
        BuyProductCallbackFactory().filter(payment_method=''),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_message_handler(
        another_product_quantity,
        state=EnterProductQuantityStates.waiting_quantity,
    )
    dispatcher.register_callback_query_handler(
        pay_with_qiwi,
        BuyProductCallbackFactory().filter(payment_method='qiwi'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        pay_with_yoomoney,
        BuyProductCallbackFactory().filter(payment_method='yoomoney'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        pay_with_minerlock,
        BuyProductCallbackFactory().filter(payment_method='minerlock'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        pay_with_coinpayments,
        BuyProductCallbackFactory().filter(payment_method='coinpayments'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        pay_with_coinbase,
        BuyProductCallbackFactory().filter(payment_method='coinbase'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
    dispatcher.register_callback_query_handler(
        pay_with_balance,
        BuyProductCallbackFactory().filter(payment_method='balance'),
        chat_type=ChatType.PRIVATE,
        state='*',
    )
